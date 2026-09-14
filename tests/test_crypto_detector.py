import unittest
from analysis.crypto_detector import detect_and_validate

class TestCryptoDetector(unittest.TestCase):
    
    def test_bitcoin_legacy(self):
        result = detect_and_validate("1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2")
        self.assertTrue(result["valid"])
        self.assertEqual(result["detected_type"], "Bitcoin")
        
    def test_bitcoin_segwit(self):
        result = detect_and_validate("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")
        self.assertTrue(result["valid"])
        self.assertEqual(result["detected_type"], "Bitcoin")
        
    def test_invalid_bitcoin(self):
        # selected chain Bitcoin but invalid format
        result = detect_and_validate("1BvBMSEYst", selected_chain="Bitcoin")
        self.assertFalse(result["valid"])
        
    def test_malformed_bitcoin(self):
        result = detect_and_validate("1BvBMS!EYstWetqTFn5Au4m4GFg7xJaNVN2") # invalid chars
        self.assertFalse(result["valid"])
        
    def test_evm_ambiguous(self):
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        result = detect_and_validate(address)
        self.assertTrue(result["valid"])
        self.assertEqual(result["detected_type"], "EVM")
        self.assertIn("Ethereum", result["possible_chains"])
        self.assertIn("BNB Smart Chain", result["possible_chains"])
        
    def test_evm_selected_chain(self):
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        result = detect_and_validate(address, selected_chain="Ethereum")
        self.assertTrue(result["valid"])
        self.assertEqual(result["detected_type"], "Ethereum")
        
    def test_invalid_evm_hex(self):
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976G" # G is invalid hex
        result = detect_and_validate(address)
        self.assertFalse(result["valid"])
        
    def test_invalid_evm_length(self):
        address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976" # 1 char short
        result = detect_and_validate(address)
        self.assertFalse(result["valid"])
        
    def test_empty_input(self):
        result = detect_and_validate("")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "Input cannot be empty.")
        
    def test_whitespace_input(self):
        result = detect_and_validate("   ")
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "Input cannot be only whitespace.")
        
    def test_random_text(self):
        result = detect_and_validate("hello_world")
        self.assertFalse(result["valid"])

    def test_tx_hash_rejected(self):
        tx_hash = "b6f6991d03df0e2e04dafffcd6bc418aac66049e2cd74b80f14ac86db1e3f0da"
        result = detect_and_validate(tx_hash)
        self.assertFalse(result["valid"])
        self.assertIn("transaction hash", result["reason"])

if __name__ == "__main__":
    unittest.main()
