import json
import requests


def pretty_print(data):
    """格式化打印 JSON 数据，让输出更清晰易读"""
    print(json.dumps(data, ensure_ascii=False, indent=2))

def health():
    resp=requests.request(method='get',
                        url="http://43.133.227.52/api/health")
    pretty_print(resp.json())

def add_cart_103():
    resp=requests.session().post(url="http://43.133.227.52/api/cart",
                                json={'productId':103,
                                'quantity':1},
                                headers={'Authorization':'Bearer practice-1-1785935635876-320d7b77cfb6e'})
    pretty_print(resp.json())

def add_cart_102():
    resp=requests.session().post(url="http://43.133.227.52/api/cart",
                                json={'productId':102,
                                'quantity':1},
                                headers={'Authorization':'Bearer practice-1-1785935635876-320d7b77cfb6e'})
    pretty_print(resp.json())

def select_cart():
    resp=requests.session().get(url="http://43.133.227.52/api/cart",
                                headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def delete_cart():
    resp=requests.session().delete(url="http://43.133.227.52/api/cart/999",
                                   headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def login():
    resp=requests.session().post(url="http://43.133.227.52/api/login",
                                 json={'username':'tester',
                                       'password':'123456'})
    return resp.json()

def get_product_list():
    resp=requests.session().get(url="http://43.133.227.52/api/products",
                                headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def health():
    resp=requests.request(method='get',
                          url="http://43.133.227.52/api/health")
    pretty_print(resp.json())

def get_cart_list():
    resp=requests.request(method='get',
                          url="http://43.133.227.52/api/cart",
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def create_order():
    resp=requests.request(method='post',
                          url='http://43.133.227.52/api/orders',
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    # required_keys=['totalAmount', 'status', 'createdAt', 'statusText']
    # for rk in required_keys:
    #     if not rk in resp.json()['order'].keys():
    #         print("失败了")
    # print(len(resp.json()['order'].keys()))

    pretty_print(resp.json())

def select_order():
    resp=requests.request(method='get',
                          url='http://43.133.227.52/api/orders',
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def select_order_by_id(id:str):
    resp=requests.request(method='get',
                          url=f'http://43.133.227.52/api/orders/{id}',
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def cancel_order():
    resp=requests.request(method='post',
                          url='http://43.133.227.52/api/orders/NO11983/cancel',
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def pay_order():
    resp=requests.request(method='post',
                          url='http://43.133.227.52/api/orders/NO11903/pay',
                          headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

def select_products():
    resp=requests.request(method='get',
                              url='http://43.133.227.52/api/products',
                              headers={'Authorization':'Bearer practice-1-1785955859995-f749412d73c96'})
    pretty_print(resp.json())

if __name__ == '__main__':
    # select_products()
    # add_cart_103()
    # add_cart_102()
    # select_cart()
    # delete_cart()
    # print(login())
    # get_product_list()
    # health()
    get_cart_list()
    # create_order()
    # select_order()
    # select_order_by_id('NO11797')
    # cancel_order()
    # pay_order()
    # health()