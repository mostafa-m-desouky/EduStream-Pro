import os
from dotenv import load_dotenv

# تحديد المسار الحالي للملف عشان يوصل لـ .env بدقة
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # 2. رابط قاعدة البيانات (بنجيبه من الـ .env)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # 3. مفتاح الأمان (بنجيبه من الـ .env)
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # 4. إيقاف ميزة التنبيهات الزائدة في SQLAlchemy لتوفير الرامات
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 5. مفاتيح Stripe (لو هنستخدمها في السيرفر)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')