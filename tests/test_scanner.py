import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.port_scanner import scan_port



class TestScanner(unittest.TestCase):
    def test_scan_port_open(self):
        # Testa se a porta 443 está aberta (exemplo)
        result = scan_port('8.8.8.8', 443, 1)
        self.assertTrue(result)  # Espera True, já que a porta 443 do Google DNS está aberta

    def test_scan_port_closed(self):
        # Testa se a porta 9999 está fechada
        result = scan_port('8.8.8.8', 9999, 1)
        self.assertFalse(result)  # Espera False, já que a porta 9999 não está aberta

    def test_scan_invalid_ip(self):
        # Testa se o IP inválido gera um erro ou False
        result = scan_port('invalid_ip', 80, 1)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
