from main import Post


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        pw=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_index(client):
    login(client, "bradleywboggs", "queso")
    response = client.get("/")
    assert response.status_code == 200


def test_delete_link_in_post(client):
    login(client, "bradleywboggs", "queso")
    response = client.get("/blog?id=7")
    # import pdb;pdb.set_trace()
    assert "Delete this post" in str(response.get_data())

def test_post_can_be_deleted(client):
    login(client, "bradleywboggs", "queso")
    assert Post.query.filter_by(id=7).first() is not None
    response = client.get("/delete?id=7")
    # import pdb;pdb.set_trace()
    assert response.status_code == 200
    assert Post.query.filter_by(id=7).first() is None