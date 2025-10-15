from flask import Blueprint, render_template, session, redirect, url_for, flash

views = Blueprint("views", __name__)

@views.route("/")
def home():
    # Eğer kullanıcı giriş yapmamışsa login sayfasına yönlendir
    if "user_email" not in session:
        flash("Önce giriş yapmalısınız.", "warning")
        return redirect(url_for("auth.login"))
    
    # Giriş yapılmışsa ana sayfayı göster
    return render_template('index.html')
