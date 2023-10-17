from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import User, Photo
from src.schemas import TransformBodyModel, PhotoTransform
import cloudinary
import cloudinary.uploader
import cloudinary.api
from src.conf.config import settings


async def transform_image(photo_id: int, body: TransformBodyModel, db: Session) -> Photo | None:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        transformation = []
        
        if body.circle.use_filter and body.circle.height and body.circle.width:
            trans_list = [{'gravity': "face", 'height': f"{body.circle.height}", 'width': f"{body.circle.width}", 'crop': "thumb"},
            {'radius': "max"}]
            [transformation.append(elem) for elem in trans_list]
        
        if body.effect.use_filter:
            effect = ""
            if body.effect.art_audrey:
                effect = "art:audrey"
            if body.effect.art_zorro:
                effect = "art:zorro"
            if body.effect.blur:
                effect = "blur:300"
            if body.effect.cartoonify:
                effect = "cartoonify"
            if effect:
                transformation.append({"effect": f"{effect}"})

        if body.resize.use_filter and body.resize.height and body.resize.height:
            crop = ""
            if body.resize.crop:
                crop = "crop"
            if body.resize.fill:
                crop = "fill"
            if crop:
                trans_list = [{"gravity": "auto", 'height': f"{body.resize.height}", 'width': f"{body.resize.width}", 'crop': f"{crop}"}]
                [transformation.append(elem) for elem in trans_list]

        if body.text.use_filter and body.text.font_size and body.text.text:
            trans_list = [{'color': "#FFFF00", 'overlay': {'font_family': "Times", 'font_size': f"{body.text.font_size}", 'font_weight': "bold", 'text': f"{body.text.text}"}}, {'flags': "layer_apply", 'gravity': "south", 'y': 20}]
            [transformation.append(elem) for elem in trans_list]

        if body.rotate.use_filter and body.rotate.width and body.rotate.degree:
            trans_list = [{'width': f"{body.rotate.width}", 'crop': "scale"}, {'angle': "vflip"}, {'angle': f"{body.rotate.degree}"}]
            [transformation.append(elem) for elem in trans_list]


        if transformation:
            trans_image = cloudinary.CloudinaryImage(photo.public_id, format="png").build_url(
                transformation=transformation
            )
            cloudinary.uploader.upload(trans_image, public_id=photo.public_id, folder="PhotoshareApp_tr")
            photo.image_transform = trans_image
            db.commit()
        return photo.image_transform
    
# async def create_link_transform_image(image_id: int, db: Session) -> str | None:
#     image = db.query(Image).filter(Image.id == image_id).first()
#     if image:
#         return image.image_transform 