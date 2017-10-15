from flask import Flask, render_template, request, redirect, url_for
from backend.client import PageClient
from backend.entity import Post
from backend.utility import get_min_schedule_date, unix_to_real_time
import time

app = Flask(__name__)

access_token = ""
page_client = PageClient(access_token)


@app.route('/')
@app.route('/home')
def home_dashboard():
    published_posts = page_client.list_published_posts()
    unpublished_posts = page_client.list_unpublished_posts()
    scheduled, unscheduled = Post.split_unpublished_posts(unpublished_posts)
    return render_template("home.html",
                           published_count=len(published_posts),
                           unpublished_count=len(unpublished_posts),
                           scheduled_posts=scheduled,
                           scheduled_count=len(scheduled),
                           page_name=page_client.page.page_name)


@app.route('/list_posts', methods=['GET'])
def list_posts():
    published_status = str(request.args.get("published_status", "All"))
    post_list = page_client.get_posts_by_published_status(request.args.get("published_status"))
    follow_message = request.args.get("follow_message")
    if not follow_message:
        follow_message = "%s posts for page %s" % (published_status.title(), page_client.page.page_name)
    return render_template("list_posts.html", post_list=post_list, follow_message=follow_message)


@app.route('/new_post', methods=["POST"])
def create_post():
    # create a new post based on the published status and scheduled time
    # if successfully created, go to the corresponding list_posts page
    parameters = dict(message=request.form.get("message"))
    # default as unpublished
    parameters["published_status"] = published_status = request.form.get("published_status", "unpublished")
    if published_status == "scheduled" and "scheduled_time" in request.form:
        parameters["scheduled_time"] = request.form.get("scheduled_time")
    success = page_client.create_post(**parameters)
    if success:
        follow_message = "Successfully created a %s post on %s" % (published_status, unix_to_real_time(int(time.time())))
        return redirect(url_for('list_posts', published_status=published_status, follow_message=follow_message))
    else:
        return redirect("/failure")


@app.route('/new_post')
def draft_post():
    return render_template("new_post.html", current_date_time=get_min_schedule_date())


@app.route('/failure')
def failure():
    return render_template("failure.html")


if __name__ == '__main__':
    app.run(host='localhost', port=7005, debug=True)

