"""[Secções 1 e 4] Ponto de entrada simples da aplicação web."""
import os

from app import app


if __name__ == "__main__":
    # Permite usar tanto "python main.py" como "python app.py".
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(port=port)
