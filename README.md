## Посилання:

https://laba1-lxy5.onrender.com

# Як запустити в себе на пк
## Набір команд:

```
git clone https://github.com/DRISCHER/BACKendLABS.git
```
```
python3 -m venv venv
```
```
source ./venv/bin/activate
```
```
pip install flask
```
```
docker build --build-arg PORT=<your port> . -t <image_name>:latest
```
```
docker run -it --rm --network=host -e PORT=<your port> <image_name>:latest
```
```
docker-compose build
```
```
docker-compose up
```
