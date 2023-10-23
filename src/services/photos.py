from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import User, Photo
from src.schemas.schemas import TransformBodyModel
import cloudinary
import cloudinary.uploader
import cloudinary.api
import qrcode
from PIL import Image
from io import BytesIO
from src.repository.photos import init_cloudinary


async def transform_image(photo_id: int, body: TransformBodyModel, user: User, db: Session ) -> Photo | None:
    """
    The transform_image function takes in a photo_id, body, user and db.
    It then initializes the cloudinary library. It queries the database for a photo with that id and user_id.
    If it finds one it creates an empty list called transformation to store all of our transformations in as dictionaries. 
    Then we check if each filter is being used by checking if its use_filter attribute is True or False (True meaning that we want to apply this filter). If so, we append the appropriate dictionary into our transformation list using either a single line or multiple lines depending on how many filters are being applied at once.
    
    :param photo_id: int: Identify the photo that is to be transformed
    :param body: TransformBodyModel: Get the data from the request body
    :param user: User: Check if the user is logged in and has access to the photo
    :param db: Session: Query the database for a photo with the id and user_id specified in the function
    :return: The image_transform url
    """
    init_cloudinary()
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
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
        else:
            return photo
        
async def create_link_transform_image(photo_id: int, user: User, db: Session) -> str | None:
    """
    The create_link_transform_image function takes in a photo_id, user and db as parameters.
    It then initializes the cloudinary library. It then queries the database for a photo with 
    the given id and user_id. If it finds one, it creates a QR code from that image's transform url 
    and uploads it to Cloudinary using its public id + '_qr' as its name (e.g., if the public id is &quot;abc&quot;, 
    then this function will upload an image named &quot;abc_qr&quot;). The function returns None if no such photo exists.
    
    :param photo_id: int: Specify the photo that you want to transform
    :param user: User: Get the user id of the user who is logged in
    :param db: Session: Access the database
    :return: A dictionary with the image_transform and qr_transform keys
    """
    init_cloudinary()
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
    if photo:
        if photo.image_transform is not None:
            qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
            qr.add_data(photo.image_transform)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            img_bytes = BytesIO()
            qr_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            qr = cloudinary.uploader.upload(img_bytes, public_id=photo.public_id+'_qr', folder="PhotoshareApp_tr")
            qr_url = cloudinary.CloudinaryImage("PhotoshareApp_tr/"+photo.public_id+'_qr', format="png").build_url(width=250, height=250, crop='fill', version=qr.get('version'))
            photo.qr_transform = qr_url
            db.commit()
            return {"image_transform": photo.image_transform, "qr_transform": photo.qr_transform}
       