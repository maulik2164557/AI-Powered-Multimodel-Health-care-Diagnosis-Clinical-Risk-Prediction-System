from app import create_app

# Create the application instance using the factory pattern defined in app/_init_.py
app = create_app()

if _name_ == "_main_":
    # In development, debug=True allows for live-reloading
    app.run(debug=True)