from flask import Flask, render_template_string, request, redirect, url_for, send_file
from faker import Faker
import io

fake = Faker()
name_list = [fake.name() for _ in range(10)]

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        new_name = None

        if request.method == "POST":
            action = request.form.get("action")

            if action == "add":
                new_name = request.form.get("new_name", "").strip()
                if new_name:
                    name_list.append(new_name)

        return render_template_string("""
            <h1>Generated and Added User List</h1>

            <!-- Add Name Form -->
            <form method="POST">
                <input type="text" name="new_name" placeholder="Enter a name" required>
                <button type="submit" name="action" value="add">Add Name</button>
            </form>

            <!-- Download File Form -->
            <form method="GET" action="{{ url_for('download') }}">
                <input type="text" name="filename" placeholder="Optional filename (e.g., names.txt)">
                <button type="submit">Download Name List</button>
            </form>

            <!-- Clear and Regenerate (goes to confirmation page) -->
            <form method="GET" action="{{ url_for('confirm_clear') }}">
                <button type="submit">Clear & Regenerate List</button>
            </form>

            <ul>
            {% for name in name_list %}
                {% if loop.last and new_name %}
                    <li><strong>{{ name }}</strong></li>
                {% else %}
                    <li>{{ name }}</li>
                {% endif %}
            {% endfor %}
            </ul>
        """, name_list=name_list, new_name=new_name)

    @app.route("/confirm-clear", methods=["GET", "POST"])
    def confirm_clear():
        if request.method == "POST":
            decision = request.form.get("decision")
            if decision == "save_clear":
                with open("name_list.txt", "w") as f:
                    for name in name_list:
                        f.write(name + "\n")
                name_list.clear()
                name_list.extend(fake.name() for _ in range(10))
                return redirect(url_for("index"))

            elif decision == "clear_only":
                name_list.clear()
                name_list.extend(fake.name() for _ in range(10))
                return redirect(url_for("index"))

            elif decision == "cancel":
                return redirect(url_for("index"))

        # GET request shows confirmation page
        return render_template_string("""
            <h2>⚠️ Are you sure you want to clear the list?</h2>
            <p>You can choose to save the current list before clearing, or cancel the action.</p>

            <form method="POST">
                <button name="decision" value="save_clear">💾 Save and Clear</button>
                <button name="decision" value="clear_only">🚫 Clear Without Saving</button>
                <button name="decision" value="cancel">❌ Cancel</button>
            </form>
        """)

    @app.route("/download", methods=["GET"])
    def download():
        filename = request.args.get("filename", "").strip() or "names.txt"

        file_buffer = io.StringIO()
        for name in name_list:
            file_buffer.write(name + "\n")
        file_buffer.seek(0)

        return send_file(
            io.BytesIO(file_buffer.getvalue().encode("utf-8")),
            mimetype="text/plain",
            as_attachment=True,
            download_name=filename
        )

    return app
