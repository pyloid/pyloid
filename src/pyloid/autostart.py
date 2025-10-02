import sys
import os

if (
	sys.platform
	== 'win32'
):
	import winreg as reg


class AutoStart:
	def __init__(
		self,
		app_name,
		app_path,
	):
		self.app_name = app_name
		self.app_path = app_path

	def set_auto_start(
		self,
		enable: bool,
	):
		if (
			sys.platform
			== 'win32'
		):
			self._set_auto_start_windows(
				enable
			)
		elif (
			sys.platform
			== 'darwin'
		):
			self._set_auto_start_macos(
				enable
			)
		elif sys.platform.startswith(
			'linux'
		):
			self._set_auto_start_linux(
				enable
			)

	def _set_auto_start_windows(
		self,
		enable: bool,
	):
		key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
		try:
			key = reg.OpenKey(
				reg.HKEY_CURRENT_USER,
				key_path,
				0,
				reg.KEY_ALL_ACCESS,
			)
			if enable:
				reg.SetValueEx(
					key,
					self.app_name,
					0,
					reg.REG_SZ,
					self.app_path,
				)
			else:
				reg.DeleteValue(
					key,
					self.app_name,
				)
			reg.CloseKey(
				key
			)
			return True
		except WindowsError:
			return False

	def _set_auto_start_macos(
		self,
		enable: bool,
	):
		plist_path = os.path.expanduser(
			f'~/Library/LaunchAgents/com.{self.app_name}.plist'
		)
		plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.{self.app_name}</string>
            <key>ProgramArguments</key>
            <array>
                <string>{self.app_path}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <false/>
        </dict>
        </plist>
        """
		try:
			if enable:
				os.makedirs(
					os.path.dirname(
						plist_path
					),
					exist_ok=True,
				)
				with (
					open(
						plist_path,
						'w',
					) as f
				):
					f.write(
						plist_content
					)
				os.chmod(
					plist_path,
					0o644,
				)
			else:
				if os.path.exists(
					plist_path
				):
					os.remove(
						plist_path
					)
			return True
		except (
			IOError,
			OSError,
		) as e:
			print(
				f'Error setting auto start on macOS: {e}'
			)
			return False

	def _set_auto_start_linux(
		self,
		enable: bool,
	):
		autostart_dir = os.path.expanduser(
			'~/.config/autostart'
		)
		desktop_file_path = os.path.join(
			autostart_dir,
			f'{self.app_name}.desktop',
		)
		desktop_content = f"""[Desktop Entry]
        Type=Application
        Exec={self.app_path}
        Hidden=false
        NoDisplay=false
        X-GNOME-Autostart-enabled=true
        Name={self.app_name}
        Comment=Pylon Application
        """
		if enable:
			os.makedirs(
				autostart_dir,
				exist_ok=True,
			)
			with (
				open(
					desktop_file_path,
					'w',
				) as f
			):
				f.write(
					desktop_content
				)
		else:
			if os.path.exists(
				desktop_file_path
			):
				os.remove(
					desktop_file_path
				)

	def is_auto_start(
		self,
	):
		if (
			sys.platform
			== 'win32'
		):
			key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
			try:
				key = reg.OpenKey(
					reg.HKEY_CURRENT_USER,
					key_path,
					0,
					reg.KEY_READ,
				)
				reg.QueryValueEx(
					key,
					self.app_name,
				)
				reg.CloseKey(
					key
				)
				return True
			except WindowsError:
				return False
		elif (
			sys.platform
			== 'darwin'
		):
			plist_path = os.path.expanduser(
				f'~/Library/LaunchAgents/com.{self.app_name}.plist'
			)
			return os.path.exists(
				plist_path
			)
		elif sys.platform.startswith(
			'linux'
		):
			desktop_file_path = os.path.expanduser(
				f'~/.config/autostart/{self.app_name}.desktop'
			)
			return os.path.exists(
				desktop_file_path
			)
		return False
