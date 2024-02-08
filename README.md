# ETH Wallet Analyzer

Interactive dashboard made with Streamlit to help you check Ethereum wallets based on their trading statistics. You only need the wallet address!

You can get some random wallets from: [Birdeye.so](https://birdeye.so/leaderboard/7D?chain=ethereum)

## Live demo
[Live dashboard uploaded to the Streamlit cloud](https://wallet-analyzer-portfolio.streamlit.app/)

## Preview
![image](https://github.com/piotrb9/wallet-analyzer/assets/157641773/2f53e7b1-44ec-4966-82a1-2afaacb2d864)
![image](https://github.com/piotrb9/wallet-analyzer/assets/157641773/647c1ebd-cc0e-4952-a9b2-2a272a868b70)
![image](https://github.com/piotrb9/wallet-analyzer/assets/157641773/1b12587a-23d4-4ee7-8658-0485bdb0fc07)
![image](https://github.com/piotrb9/wallet-analyzer/assets/157641773/148476c8-f162-4098-9e8f-e37d1ca945fd)
![image](https://github.com/piotrb9/wallet-analyzer/assets/157641773/d14f6f79-745d-4e95-9cda-73ed1fd3d835)

## Installation
Get etherscan.io API key from: https://docs.etherscan.io/getting-started/viewing-api-usage-statistics

Set env variable with your api key:
```bash
export etherscan_api_key="YOUR API KEY"
```


Install the requirements
```bash
pip install -r requirements.txt
```

Download the repo on your local machine and run the src/run_dashboard.py file

```bash
python src/run_dashboard.py
```

## Usage
The panel will automatically open in your browser locally, if not check the output for the link and use it in your browser.
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://11.1.1.2:8501
```

All features are described in the panel when you hover them. You only have to write an Ethereum wallet address in the top input field. There must be at least 1 proper transaction to make the panel work properly

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## TODO
Read the [TODO](https://github.com/piotrb9/wallet-analyzer/blob/master/TODO.md) to see the list.

## License

[MIT](https://choosealicense.com/licenses/mit/)

Powered by Etherscan.io APIs
