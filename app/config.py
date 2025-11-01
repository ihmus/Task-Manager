import os

DB_NAME = "task_management.db"
DB_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "db")
DB_PATH = os.path.join(DB_DIR, DB_NAME)


""" önceden yazılan index.html kodları kaybolmasın diye buraya yazdım schule!

{% extends "base.html" %} {% block title %}Ana Sayfa{% endblock %} {% block
content %}

<div class="flex-1 p-8">
  <!-- Notlar -->

  <!-- Not Ekleme Formu -->
  <form method="POST" class="mt-4">
    <textarea
      name="note"
      id="note"
      class="w-full border rounded-md p-2"
      placeholder="Yeni not ekle..."
    ></textarea>
    <div class="text-center mt-2">
      <button
        type="submit"
        class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
      >
        Not Ekle
      </button>
    </div>
  </form>
</div>

{% endblock %} {% block javascript %}
<script>
  function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then(() => window.location.reload());
  }
</script>
{% endblock %} 

"""