from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Flask-Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "vigneshwaranb.22cse@kongu.edu"
app.config["MAIL_PASSWORD"] = "hsfr jmfj iiic oyah"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        # Get the PDF file from the request
        pdf_file = request.files["pdf"]
        recipient_email = "vigneshsobalamurugan2005@gmail.com"  # Set the recipient's email address

        # Create the email message
        msg = Message(
            "Transaction History PDF",
            sender="vigneshwaranb.22cse@kongu.edu",
            recipients=[recipient_email],
        )
        msg.body = "Please find the attached Transaction History PDF."

        # Attach the PDF
        msg.attach(
            pdf_file.filename,
            "application/pdf",
            pdf_file.read(),
        )

        # Send the email
        mail.send(msg)

        return jsonify({"message": "Email sent successfully!"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to send email."}), 500

if __name__ == "__main__":
    app.run(debug=True)
