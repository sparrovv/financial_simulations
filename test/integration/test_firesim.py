from streamlit.testing.v1 import AppTest


def test_app_doesnt_blow_up():
    at = AppTest.from_file("firesim.py")
    at.run()
    assert not at.exception
