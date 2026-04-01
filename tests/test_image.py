import io
import pytest
from unittest.mock import MagicMock, patch
from services.image_service import save_image, get_user_images, update_image, delete_image
from models.image_tags_model import ImageTag
from models.image_model import Image

class DummyUser:
    def __init__(self, id):
        self.id = id

class DummyFile:
    def __init__(self, filename, content_type, content):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(content)

class DummyImage(Image):
    def __init__(self, id, user_id, file_path="path.png"):
        self.id = id
        self.user_id = user_id
        self.file_path = file_path
        self.is_deleted = False
        self.tags = []


def test_save_image_success():
    db = MagicMock()
    current_user = DummyUser(id=1)
    category_id = 1
    tags = "nature,sunset"
    dummy_file = DummyFile("test.png", "image/png", b"dummy data")

    db.query().filter().first.return_value = MagicMock(id=category_id)

    with patch("os.path.exists", return_value=True), \
         patch("shutil.copyfileobj"), \
         patch("uuid.uuid4", return_value="fixed-uuid"):

        image = save_image(dummy_file, current_user, category_id, tags, db)

        db.add.assert_called()
        db.add_all.assert_called()
        db.commit.assert_called()
        db.refresh.assert_called()

        assert image.user_id == current_user.id
        assert image.file_path.endswith("fixed-uuid.png")

        added_tags = db.add_all.call_args[0][0]
        tag_values = [t.tag for t in added_tags]
        assert tag_values == ["nature", "sunset"]
        assert all(t.image_id == image.id for t in added_tags)


def test_save_image_invalid_file_type():
    db = MagicMock()
    current_user = DummyUser(id=1)
    dummy_file = DummyFile("test.txt", "text/plain", b"fake data")

    with pytest.raises(Exception) as exc:
        save_image(dummy_file, current_user, 1, None, db)

    assert "Invalid file type" in str(exc.value)


def test_save_image_category_not_found():
    db = MagicMock()
    current_user = DummyUser(id=1)
    dummy_file = DummyFile("test.png", "image/png", b"fake data")

    db.query().filter().first.return_value = None 

    with pytest.raises(Exception) as exc:
        save_image(dummy_file, current_user, 999, None, db)

    assert "Category not found" in str(exc.value)


def test_get_user_images():
    db = MagicMock()
    current_user = DummyUser(id=1)

    dummy_images = [DummyImage(id=i, user_id=1) for i in range(3)]
    db.query().filter().options().order_by().offset().limit().all.return_value = dummy_images

    images = get_user_images(current_user, db, page=1)
    assert len(images) == 3
    for img in images:
        assert img.user_id == current_user.id


def test_update_image_file_and_tags():
    db = MagicMock()
    current_user = DummyUser(id=1)
    dummy_image = DummyImage(id=1, user_id=1, file_path="old.png")
    db.query().filter().first.return_value = dummy_image

    new_file = DummyFile("new.jpg", "image/jpeg", b"new data")
    new_tags = "mountain,forest"

    with patch("os.path.exists", return_value=True), \
         patch("os.remove"), \
         patch("shutil.copyfileobj"), \
         patch("uuid.uuid4", return_value="uuid123"):

        updated_image = update_image(
            image_id=1,
            file=new_file,
            current_user=current_user,
            db=db,
            category_id=2,
            tags=new_tags
        )

        assert updated_image.category_id == 2
        assert updated_image.file_path.endswith("uuid123.jpg")
        db.add_all.assert_called()
        db.commit.assert_called()
        db.refresh.assert_called()


def test_delete_image():
    db = MagicMock()
    current_user = DummyUser(id=1)
    dummy_image = DummyImage(id=1, user_id=1)
    db.query().filter().first.return_value = dummy_image

    deleted_image = delete_image(1, current_user, db)
    assert deleted_image.is_deleted is True
    db.commit.assert_called()
    db.refresh.assert_called()