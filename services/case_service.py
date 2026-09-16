import logging
import datetime
import json
from typing import List, Optional, Dict, Any
from database.connection import get_connection
from analysis.case_models import (
    Case, CaseWallet, CaseTransaction, CaseAlert, 
    CaseEvidence, CaseSummary, CaseStatus, CasePriority
)

logger = logging.getLogger(__name__)

class CaseService:
    def __init__(self):
        pass

    def _generate_case_number(self, cursor) -> str:
        """Deterministically generate the next available case number."""
        year = datetime.datetime.now(datetime.timezone.utc).year
        cursor.execute("SELECT case_number FROM cases WHERE case_number LIKE ? ORDER BY case_number DESC LIMIT 1", (f"CNX-{year}-%",))
        row = cursor.fetchone()
        if row:
            try:
                last_num = int(row[0].split('-')[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1
            
        return f"CNX-{year}-{next_num:04d}"

    def create_case(self, title: str, description: str = "", priority: str = "MEDIUM", 
                    primary_wallet: Optional[str] = None, primary_blockchain: Optional[str] = None, 
                    notes: Optional[str] = None, created_by: str = "Analyst") -> Optional[Case]:
        conn = get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            case_number = self._generate_case_number(cursor)
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO cases (case_number, title, description, status, priority, created_at, updated_at, created_by, primary_wallet, primary_blockchain, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (case_number, title, description, CaseStatus.OPEN.value, priority, now, now, created_by, primary_wallet, primary_blockchain, notes))
            
            case_id = cursor.lastrowid
            
            # If primary wallet provided, add it as a CaseWallet immediately
            if primary_wallet and primary_blockchain:
                try:
                    cursor.execute("""
                        INSERT INTO case_wallets (case_id, wallet_address, blockchain, role, added_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (case_id, primary_wallet, primary_blockchain, "PRIMARY_TARGET", now))
                except Exception as e:
                    logger.warning(f"Failed to attach primary wallet: {e}")
                    
            conn.commit()
            return self.get_case(case_id)
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_case(self, case_identifier) -> Optional[Case]:
        """Fetch case by ID or Case Number."""
        conn = get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            if isinstance(case_identifier, int) or str(case_identifier).isdigit():
                cursor.execute("SELECT * FROM cases WHERE id = ?", (int(case_identifier),))
            else:
                cursor.execute("SELECT * FROM cases WHERE case_number = ?", (str(case_identifier),))
                
            row = cursor.fetchone()
            if not row:
                return None
                
            # Maps row to dict
            cols = [desc[0] for desc in cursor.description]
            row_dict = dict(zip(cols, row))
            
            case = Case(**row_dict)
            
            # Fetch relations
            case.wallets = self._get_case_wallets(cursor, case.id)
            case.transactions = self._get_case_transactions(cursor, case.id)
            case.alerts = self._get_case_alerts(cursor, case.id)
            case.evidence = self._get_case_evidence(cursor, case.id)
            
            return case
        except Exception as e:
            logger.error(f"Error fetching case {case_identifier}: {e}")
            return None
        finally:
            conn.close()
            
    def _get_case_wallets(self, cursor, case_id: int) -> List[CaseWallet]:
        cursor.execute("SELECT * FROM case_wallets WHERE case_id = ?", (case_id,))
        cols = [desc[0] for desc in cursor.description]
        return [CaseWallet(**dict(zip(cols, row))) for row in cursor.fetchall()]

    def _get_case_transactions(self, cursor, case_id: int) -> List[CaseTransaction]:
        cursor.execute("SELECT * FROM case_transactions WHERE case_id = ?", (case_id,))
        cols = [desc[0] for desc in cursor.description]
        return [CaseTransaction(**dict(zip(cols, row))) for row in cursor.fetchall()]

    def _get_case_alerts(self, cursor, case_id: int) -> List[CaseAlert]:
        cursor.execute("SELECT * FROM case_alerts WHERE case_id = ?", (case_id,))
        cols = [desc[0] for desc in cursor.description]
        return [CaseAlert(**dict(zip(cols, row))) for row in cursor.fetchall()]

    def _get_case_evidence(self, cursor, case_id: int) -> List[CaseEvidence]:
        cursor.execute("SELECT * FROM case_evidence WHERE case_id = ?", (case_id,))
        cols = [desc[0] for desc in cursor.description]
        return [CaseEvidence(**dict(zip(cols, row))) for row in cursor.fetchall()]

    def list_cases(self) -> List[Case]:
        conn = get_connection()
        if not conn:
            return []
            
        cases = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cases ORDER BY updated_at DESC")
            cols = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                cases.append(Case(**dict(zip(cols, row))))
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
        finally:
            conn.close()
        return cases

    def update_case(self, case_id: int, **kwargs) -> bool:
        """Update case fields."""
        allowed_fields = {"title", "description", "status", "priority", "notes", "primary_wallet", "primary_blockchain"}
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed_fields:
                updates.append(f"{k} = ?")
                values.append(v)
                
        if not updates:
            return False
            
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updates.append("updated_at = ?")
        values.append(now)
        values.append(case_id)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE cases SET {', '.join(updates)} WHERE id = ?", tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def _touch_case(self, cursor, case_id: int):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute("UPDATE cases SET updated_at = ? WHERE id = ?", (now, case_id))

    def close_case(self, case_id: int) -> bool:
        return self.update_case(case_id, status=CaseStatus.CLOSED.value)
        
    def reopen_case(self, case_id: int) -> bool:
        return self.update_case(case_id, status=CaseStatus.OPEN.value)
        
    def delete_case(self, case_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def add_wallet_to_case(self, case_id: int, wallet_address: str, blockchain: str, label: Optional[str] = None, role: str = "RELATED") -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO case_wallets (case_id, wallet_address, blockchain, label, role, added_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (case_id, wallet_address, blockchain, label, role, now))
            self._touch_case(cursor, case_id)
            conn.commit()
            return True
        except Exception as e:
            logger.warning(f"Error attaching wallet {wallet_address} to case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_wallet_from_case(self, case_id: int, wallet_address: str, blockchain: str) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM case_wallets WHERE case_id = ? AND wallet_address = ? AND blockchain = ?", (case_id, wallet_address, blockchain))
            if cursor.rowcount > 0:
                self._touch_case(cursor, case_id)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing wallet from case: {e}")
            return False
        finally:
            conn.close()
            
    def add_transaction_to_case(self, case_id: int, tx_hash: str, blockchain: str, relationship: str = "UNKNOWN") -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO case_transactions (case_id, tx_hash, blockchain, relationship, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, (case_id, tx_hash, blockchain, relationship, now))
            self._touch_case(cursor, case_id)
            conn.commit()
            return True
        except Exception as e:
            logger.warning(f"Error attaching transaction {tx_hash} to case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_transaction_from_case(self, case_id: int, tx_hash: str, blockchain: str) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM case_transactions WHERE case_id = ? AND tx_hash = ? AND blockchain = ?", (case_id, tx_hash, blockchain))
            if cursor.rowcount > 0:
                self._touch_case(cursor, case_id)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing transaction from case: {e}")
            return False
        finally:
            conn.close()
            
    def attach_alert_to_case(self, case_id: int, alert_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO case_alerts (case_id, alert_id, added_at)
                VALUES (?, ?, ?)
            """, (case_id, alert_id, now))
            self._touch_case(cursor, case_id)
            conn.commit()
            return True
        except Exception as e:
            logger.warning(f"Error attaching alert {alert_id} to case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_evidence(self, case_id: int, evidence_type: str, title: str, description: str, 
                     source: str, source_type: str, data_mode: str, 
                     reference_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            meta_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO case_evidence (case_id, evidence_type, reference_id, title, description, source, source_type, data_mode, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (case_id, evidence_type, reference_id, title, description, source, source_type, data_mode, now, meta_json))
            self._touch_case(cursor, case_id)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding evidence to case {case_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def remove_evidence(self, evidence_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # Find case_id to touch it
            cursor.execute("SELECT case_id FROM case_evidence WHERE id = ?", (evidence_id,))
            row = cursor.fetchone()
            if not row:
                return False
                
            case_id = row[0]
            cursor.execute("DELETE FROM case_evidence WHERE id = ?", (evidence_id,))
            self._touch_case(cursor, case_id)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing evidence {evidence_id}: {e}")
            return False
        finally:
            conn.close()
            
    def get_case_summary(self, case_id: int) -> Optional[CaseSummary]:
        case = self.get_case(case_id)
        if not case:
            return None
            
        blockchains = set([w.blockchain for w in case.wallets])
        blockchains.update([t.blockchain for t in case.transactions])
        if case.primary_blockchain:
            blockchains.add(case.primary_blockchain)
            
        return CaseSummary(
            case_id=case_id,
            num_wallets=len(case.wallets),
            num_transactions=len(case.transactions),
            num_alerts=len(case.alerts),
            num_evidence=len(case.evidence),
            observed_blockchains=list(blockchains),
            latest_activity=case.updated_at,
            current_risk_score=None, # Injected by risk engine if desired, or left as None
            latest_monitoring_status=None # To be populated by UI or orchestrator
        )
