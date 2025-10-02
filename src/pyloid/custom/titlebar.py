from PySide6.QtWidgets import (
	QWidget,
	QHBoxLayout,
	QLabel,
	QPushButton,
	QVBoxLayout,
	QApplication,
)
from PySide6.QtGui import (
	QColor,
	QPalette,
	QPixmap,
)
from PySide6.QtCore import (
	Qt,
)


class CustomTitleBar(
	QWidget
):
	def __init__(
		self,
		parent=None,
	):
		super().__init__(
			parent
		)
		self.layout = QHBoxLayout(
			self
		)
		self.layout.setContentsMargins(
			5,
			0,
			5,
			0,
		)
		self.layout.setSpacing(
			0
		)

		self.icon_label = QLabel()
		self.icon_label.setFixedSize(
			20,
			20,
		)
		self.title = QLabel(
			'Custom Title'
		)

		self.minimize_button = QPushButton(
			'－'
		)
		self.maximize_button = QPushButton(
			'❐'
		)
		self.close_button = QPushButton(
			'×'
		)

		for button in (
			self.minimize_button,
			self.maximize_button,
			self.close_button,
		):
			button.setFixedSize(
				45,
				30,
			)
			button.setFlat(
				True
			)

		self.layout.addWidget(
			self.icon_label
		)
		self.layout.addSpacing(
			5
		)
		self.layout.addWidget(
			self.title
		)
		self.layout.addStretch(
			1
		)
		self.layout.addWidget(
			self.minimize_button
		)
		self.layout.addWidget(
			self.maximize_button
		)
		self.layout.addWidget(
			self.close_button
		)

		self.minimize_button.clicked.connect(
			self.window().showMinimized
		)
		self.maximize_button.clicked.connect(
			self.toggle_maximize
		)
		self.close_button.clicked.connect(
			self.window().close
		)

		self.setFixedHeight(
			30
		)
		self.set_style(
			'darkblue',
			'white',
		)

	def set_style(
		self,
		bg_color,
		text_color,
	):
		self.setAutoFillBackground(
			True
		)
		palette = self.palette()
		bg_qcolor = QColor(
			bg_color
		)
		text_qcolor = QColor(
			text_color
		)
		palette.setColor(
			QPalette.Window,
			bg_qcolor,
		)
		palette.setColor(
			QPalette.WindowText,
			text_qcolor,
		)
		self.setPalette(
			palette
		)

		self.title.setStyleSheet(
			f'color: {text_color}; font-weight: bold;'
		)

		button_style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                font-family: Arial;
                font-size: 14px;
                padding: 0px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {bg_qcolor.lighter(120).name()};
            }}
            QPushButton:pressed {{
                background-color: {bg_qcolor.darker(110).name()};
            }}
        """
		for button in (
			self.minimize_button,
			self.maximize_button,
			self.close_button,
		):
			button.setStyleSheet(
				button_style
			)

		self.close_button.setStyleSheet(
			button_style
			+ f"""
            QPushButton:hover {{
                background-color: #e81123;
                color: white;
            }}
        """
		)

	def mousePressEvent(
		self,
		event,
	):
		if (
			event.button()
			== Qt.LeftButton
		):
			self.window().moving = True
			self.window().offset = event.pos()

	def mouseMoveEvent(
		self,
		event,
	):
		if self.window().moving:
			self.window().move(
				event.globalPos()
				- self.window().offset
			)

	def mouseReleaseEvent(
		self,
		event,
	):
		if (
			event.button()
			== Qt.LeftButton
		):
			self.window().moving = False

	def toggle_maximize(
		self,
	):
		if self.window().isMaximized():
			self.window().showNormal()
			self.maximize_button.setText(
				'❐'
			)
		else:
			self.window().showMaximized()
			self.maximize_button.setText(
				'❐'
			)

	def set_icon(
		self,
		icon_path,
	):
		pixmap = QPixmap(
			icon_path
		)
		self.icon_label.setPixmap(
			pixmap.scaled(
				20,
				20,
				Qt.KeepAspectRatio,
				Qt.SmoothTransformation,
			)
		)

	def set_title(
		self,
		title,
	):
		self.title.setText(
			title
		)
