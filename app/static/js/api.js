let burl = 'https://api.binance.com';

let query = '/api/v3/ticker/24hr';
//API Guide: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book
//24 hour rolling window price change statistics：/api/v3/ticker/24hr
//Market Data endpoints： /api/v3/depth


query += '?symbol=BTCUSDT';

let url = burl + query;
    
var proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    
fetch(proxyUrl + url)
  .then(blob => blob.json())
  .then(data => {
    console.table(data);
    return data;
  })
  .catch(e => {
    console.log(e);
    return e;
  });