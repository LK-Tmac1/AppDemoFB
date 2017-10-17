from flask import Flask, render_template, request, redirect, url_for
from backend.client import PageClient
from backend.entity import Post
from backend.utility import get_min_schedule_date, unix_to_real_time
import time, facebook

app = Flask(__name__)
page_client = PageClient()


def handle_error(error_message):
    # if an error happens and it is about active access token, redirect to login
    # otherwise return to failure.html and print the error message
    error_message = str(error_message)
    if error_message.find("access") >= 0 and error_message.find("token") >= 0:
        return redirect(url_for("login", login_message="Access token invalid now, please re-enter."))
    return render_template("failure.html", error_message=error_message)


@app.route('/')
@app.route('/login')
def login():
    login_message = request.args.get("login_message", "Please input your page access token")
    return render_template("login.html", login_message=login_message)


@app.route('/', methods=['POST'])
@app.route('/login', methods=['POST'])
def auth():
    access_token = request.form.get("access_token")
    try:
        page_client.update_token(access_token)
        return redirect("/home")
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/home')
def home_dashboard():
    try:
        published_posts = page_client.list_published_posts()
        unpublished_posts = page_client.list_unpublished_posts()
        scheduled, unscheduled = Post.split_unpublished_posts(unpublished_posts)
        return render_template("home.html",
                               published_count=len(published_posts),
                               unpublished_count=len(unpublished_posts),
                               scheduled_count=len(scheduled),
                               page_name=page_client.page.page_name)
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/list_posts', methods=['GET'])
def list_posts():
    try:
        published_status = str(request.args.get("published_status", "all")).lower()
        post_list = page_client.get_posts_by_published_status(published_status)
        follow_message = request.args.get("follow_message")
        show_stat = published_status == "all" or published_status == "published"
        if not follow_message:
            follow_message = "%s posts for page %s" % (published_status.title(), page_client.page.page_name)
        return render_template("list_posts.html", post_list=post_list,
                               follow_message=follow_message, show_stat=show_stat)
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/list_posts', methods=['POST'])
def update_post():
    try:
        post_id = request.form.get("edit")
        return redirect(url_for('get_post_to_edit', post_id=post_id))
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/edit_post', methods=['GET'])
def get_post_to_edit():
    try:
        post = page_client.get_target_post(request.args.get("post_id"))
        if post:
            return render_template("edit_post.html", post=post)
        else:
            return handle_error(error_message="This post does not exist!")
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/edit_post', methods=['POST'])
def submit_update_post():
    try:
        if 'edit' in request.form:
            # If the post is already published, cannot change it to unpublished or scheduled anymore.
            published_status = "published"
            if "post_id" not in request.form:
                raise facebook.GraphAPIError("Not valid post ID to be updated.")
            parameters = dict(message=request.form.get("message"), post_id=request.form.get("post_id"),
                            published_status="published")
            if "published_status" in request.form:
                parameters["published_status"] = published_status = request.form.get("published_status")
                if published_status == "scheduled" and "scheduled_time" in request.form:
                    parameters["scheduled_time"] = request.form.get("scheduled_time", 0)
            response = page_client.create_post(**parameters)
            if 'success' in response:
                display_post_content = str(parameters["message"])
                if len(display_post_content) >= 20:
                    display_post_content = display_post_content[:20] + "...(ignored)"
                follow_message = "Successfully updated the post."
                return redirect(url_for('list_posts', published_status=published_status, follow_message=follow_message))
            else:
                return redirect(url_for("failure", error_message=response))
        elif 'delete' in request.form:
            page_client.delete_post(request.form.get("post_id"))
            follow_message = "Successfully deleted the post"
            return redirect(url_for('list_posts', follow_message=follow_message))
    except facebook.GraphAPIError as e:
        return handle_error(e.message)


@app.route('/new_post')
def draft_post():
    return render_template("new_post.html", current_date_time=get_min_schedule_date())


@app.route('/new_post', methods=["POST"])
def submit_new_post():
    # create a new post based on the published status and scheduled time
    # if successfully created, go to the corresponding list_posts page
    parameters = dict(message=request.form.get("message"))
    # default as unpublished
    parameters["published_status"] = published_status = request.form.get("published_status", "unpublished")
    if published_status == "scheduled" and "scheduled_time" in request.form:
        parameters["scheduled_time"] = request.form.get("scheduled_time")
    try:
        response = page_client.create_post(**parameters)
        if 'id' in response and 'error' not in response:
            follow_message = "Successfully created a %s post on %s" % (published_status, unix_to_real_time(int(time.time())))
            return redirect(url_for('list_posts', published_status=published_status, follow_message=follow_message))
        else:
            return handle_error(error_message=response)
    except facebook.GraphAPIError as e:
        return handle_error(error_message=e.message)


if __name__ == '__main__':
    app.run(host='localhost', port=7005, debug=True)
