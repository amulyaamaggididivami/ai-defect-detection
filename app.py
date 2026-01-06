from fasthtml.common import *
from routes import home_page, preview_handler, analyze_handler

# Initialize the FastHTML app
app, rt = fast_app(
    pico=False,
    hdrs=(
        Link(rel="stylesheet", href="/static/style.css"),
        Script(src="https://unpkg.com/lucide@latest"),
    )
)

# Define routes
@rt("/")
def get():
    return home_page()

@rt("/preview")
async def post(image: UploadFile):
    return await preview_handler(image)

@rt("/analyze")
async def post(filename: str):
    return await analyze_handler(filename)

# Start the server
if __name__ == "__main__":
    serve()