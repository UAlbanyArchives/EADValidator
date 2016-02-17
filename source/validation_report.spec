# -*- mode: python -*-
a = Analysis(['C:\\Projects\\EADValidator\\validation_report.py'],
             pathex=['C:\\Python27\\Scripts'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
		  a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'), ('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')]
		  if sys.platform == 'win32' else a.binaries,
		  a.datas + [('ead.xsd', 'ead.xsd', 'DATA'), ('ead.dtd', 'ead.dtd', 'DATA')],
          name='validation_report.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='validation_report')
