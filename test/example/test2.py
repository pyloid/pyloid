from pyloid import (
	Pyloid,
)

app = Pyloid(
	app_name='pyloid-app'
)

window = app.create_window(
	'border-radius and transparent',
	frame=False,
	width=500,
	height=500,
)

html = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      html,
      body {
        margin: 0;
        padding: 0;
      }
      #main {
        width: 100vw;
        height: 100vh;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

    </style>
  </head>
  <body>
    <div id="main" data-pyloid-drag-region>
      Hello World!
    </div>
  </body>
</html>
"""

window.load_html(
	html
)
window.show_and_focus()

app.run()
