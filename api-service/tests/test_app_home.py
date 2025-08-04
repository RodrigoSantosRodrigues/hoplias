from run import helth

def test_handler():
    response = helth()
    assert response == {"message": "ok"}
