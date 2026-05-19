from models.database import db
from models import ImageSchema, ImageModel

class ImageController:
    
    def __init__(self):
        self.schema = ImageSchema
        self.model = ImageModel

    def createImage(self, data: dict) -> ImageModel:
        try:
            new_image = ImageModel(**data)
            db.session.add(new_image)
            db.session.commit()
            return new_image
        except Exception as e:
            db.session.rollback()
            raise e
        
    def getImageByImageId(self, image_id: str) -> ImageModel | None:
        try:
            image = self.model.query.filter_by(image_id=image_id).first()
            if image:
                return image
            return None
        except Exception as e:
            raise e
    
image_controller = ImageController()