def text_parse_mode(text):
    symbols = '.,—!()+-*'
    for symbol in symbols:
        text = text.replace(symbol, '\\' + symbol)
    return text