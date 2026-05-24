import requests

url = 'https://sb-pro.skydropx.com/api/v1/address_templates'
headers = {"Content-Type":"application/json","Authorization":"Bearer gFA20N781QCgE9GkN2icghdvvp+y4iaAeqDCjavYie2pH9/X86ZvNSn0U8JHYsN8Yg3GoDB2jec45g5mJOn3l7i2ytYH1srR4BRX6AE02N0d4zSNSbPWTT+h11HLqNSaZLl+uBAC/WVh3UEiFI0M0MbUfrr6WDszwi73JQyLwLb93TVYrG32tax9XlyHtm2iSphAIUrA8U+EokERXrtmz/2+FjGvYaLr8c2MEVgTsYFigDCqnK07aoYC1R+wxbzlEmPYRmAtZXJVYNXWMOQLUUoXpR/g6GlSOKhgcZJXuGUKS+2qHrm0/CK/Nhf919IPAypxrqPR/fxul2Gw12TUAm+YS3QKsm0fbQoQL3N+V+NkYGK5FuEGpd1Tg05EmRjR/tNLhnXZoR9B9Xu9HdUDn+lJH+isAmWWwUXCgNiqqJ//4TJN+zuc9WFjDpQ3--GyYrVB3LCzsVHy5t--/00Ymm24OlY4zKMWNNssBA=="}


response = requests.get(url, headers=headers)
print(response.text)