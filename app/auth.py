from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint("auth", __name__)

# Örnek kullanıcı verisi: email -> parola_hash
users = {
    "ali@example.com": generate_password_hash("123456"),
    "veli@example.com": generate_password_hash("password")
}

@auth.route("/login", methods=["GET", "POST"])
def login():
    context = {
        "text": "deneme",
        "is_showing": True
    }

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user_hash = users.get(email)
        if user_hash and check_password_hash(user_hash, password):
            session.clear()
            session["user_email"] = email
            flash("Giriş başarılı!", "success")
            return redirect(url_for("views.home"))  # Dashboard veya ana sayfa route'unu ayarla
        else:
            flash("E-posta veya parola yanlış!", "danger")
            # context'i tekrar gönderiyoruz, formda hata mesajı gösterilecek
            return render_template("login.html", **context)

    # GET isteğinde formu göster
    return render_template("login.html", **context)
