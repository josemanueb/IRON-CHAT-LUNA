#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hash_utils import verify_project_integrity

project_dir = os.path.dirname(os.path.abspath(__file__))
icon, msg = verify_project_integrity(project_dir)
print("="*50)
print("🔐 VERIFICACION DE INTEGRIDAD")
print("="*50)
print(f"  {icon} {msg}")
print("="*50)
sys.exit(0 if icon == "✅" else 1)
