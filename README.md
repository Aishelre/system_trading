
# system_trading

# Requirements
- python 3.x (32bit)
- PyQt 5
- Pyro 4

# Usage
1. <code>python main_trading.py</code> (in 32bit env)
2. <p><code>python prediction-server.py</code> (in 64bit env)</p>
3. Enter Pyro Url from <code>prediction-server.py</code> in <code>main_trading.py</code>



## GUI
![gui](https://user-images.githubusercontent.com/24665474/33056999-e8a92ae2-cecb-11e7-8412-76fa47777dc5.PNG)

### - 사용한 전략의 기저 이론
  1. 주가는 여러 요소의 영향을 받지만 이들 요소는 매매라는 방법을 거쳐야 수익으로 발생될 수 있다.
  2. 시장 원리에 따라서 매수가 많으면 주가가 올라가고 매도가 많으면 주가는 내려간다.
  3. 매수, 매도 물량의 변화량을 머신러닝을 이용하여 n초 후 주가가 오를 지 예측한다.

## Precision and Recall (used one of the models)
### prediction using Trained data
![trained](https://user-images.githubusercontent.com/24665474/33057014-fd36b0b0-cecb-11e7-9630-f4a4bf690a7f.png)
### prediction using Untrained data
![not trained](https://user-images.githubusercontent.com/24665474/33057025-06766832-cecc-11e7-87c2-f5c2abb26f29.png)
### prediction (code : 000660)
![000660](https://user-images.githubusercontent.com/24665474/33062137-93880f4a-cee1-11e7-8ad2-10308b9f3a4f.png)

### 000660의 데이터로만 트레이닝한 뒤 예측한 결과
한 종목 특유의 매매 패턴이 존재하지 않을까 생각하였으나
이 역시 예측이 잘 안됨. precision 0.6 내외의 결과를 보임

<hr>

### - 한계
1. 주식종목의 다양함과 종목들간의 매매 패턴과 거래량 등의 차이가 있음. 이 때문에 general한 모델을 생성하기 어려움.
2. 종목들간의 주가 변동성 차이와, 주식 자체의 변동성 때문에 가격이 오름을 예측해도 매매 가격에 비해 적은 수익이 생김.
    - 해결 : 1초 간격 데이터가 아닌 x분 데이터를 사용하고 n개 호가 이상 뛰는 case로 training한다.
            (시간 간격이 클 경우 전처리 방법을 바꿔야함)
3. 기업에 대한 기본적 분석이 주가에 영향을 줄 수 있으나 현재 매매 전략은 이를 전혀 반영하지 않음. 
4. 약 6시간동안 개장되는 주식시장에 비해 가상화폐 시장은 24시간 개장이므로 보다 적합한 시장이 존재함
5. 주문에 따른 주가의 연속적인 변동이 작음.

### TODO
- preprocessing 방법 변경
- 호가 데이터 이외의 데이터 사용
