"""Simple traders dashboard with Streamlit"""
import pandas as pd
import plotly.express as px
import streamlit as st
from io import StringIO
import base64
from wallet_analyzer_eth import WalletAnalyzer
from wallet_analyzer_eth import MetricsCalculator


class Dashboard:
    """
    Dashboard class to create a simple traders dashboard with Streamlit.
    """
    def __init__(self, initial_wallet_address: str):
        self.txs_df = None
        self.swap_txs_df = None
        self.token_trades_df = None
        self.tokens_txs_df = None
        self.wallet_analyzer = None
        self.metrics_calculator = None
        self.wallet_address = initial_wallet_address

    def get_wallet_data(self, wallet_address: str) -> None:
        """
        Get wallet data and calculate all the metrics

        :param wallet_address: Wallet address
        :return: None
        """
        wallet_analyzer = WalletAnalyzer(wallet_address)
        wallet_analyzer.get_data()
        wallet_analyzer.calculate_swap_txs()
        wallet_analyzer.check_token_transfers()
        wallet_analyzer.check_internal_transfers()
        wallet_analyzer.check_snipers()

        self.wallet_analyzer = wallet_analyzer

        self.swap_txs_df = wallet_analyzer.get_swap_txs()
        self.txs_df = wallet_analyzer.txs_df
        self.token_trades_df = wallet_analyzer.calculate_tokens_txs()

        self.metrics_calculator = MetricsCalculator(self.swap_txs_df, self.txs_df, self.token_trades_df)

    def main(self) -> None:
        """
        Main function to run the dashboard

        :return: None
        """
        st.set_page_config(
            page_title="Wallet analysis",
            page_icon="✅",
            layout="wide",
        )

        st.markdown("### Wallet address")
        self.wallet_address = st.text_input("Enter the wallet address", self.wallet_address)

        # Data
        self.get_wallet_data(self.wallet_address)
        total_eth_in, total_eth_internal_in, total_eth_out, total_eth_buy, total_eth_sell, total_stablecoins_in,\
            total_stablecoins_out, total_fees_eth, count_tokens_in,\
            count_tokens_out = self.metrics_calculator.calculate_total_values()

        final_trade_result = self.metrics_calculator.final_trade_result()
        snipes_percent = self.metrics_calculator.snipes_percent()
        avg_trade_size = self.metrics_calculator.avg_trade_size()
        avg_trade_result = self.metrics_calculator.avg_trade_result()

        # Charts
        trades_per_day_df = self.metrics_calculator.trades_per_day()
        cum_res_df = self.metrics_calculator.cumulated_daily_trading_result()

        # Dataframes
        transactions_df = self.txs_df.copy()
        transactions_df['dateTime'] = pd.to_datetime(transactions_df.loc[:, 'timeStamp'], unit='s')
        transactions_df = transactions_df.loc[:, ['dateTime', 'hash', 'from', 'to', 'value', 'gasPrice', 'txType',
                                                  'swapType', 'swapEth', 'tokenValue', 'tokenName', 'tokenSymbol',
                                                  'tokenCa', 'snipe', 'txFee']]

        placeholder = st.empty()

        with placeholder.container():
            kpi10, kpi20, kpi30, kpi40 = st.columns(4)

            kpi10.metric(
                label="Final trade result (only buy+sell txs)",
                value=f"{round(final_trade_result, 3)} ETH",
                help="Final trade result based on the trades detailed view dataframe (below), only for tokens that "
                     "have both buy and sell txs, so tokens that are not sold yet are not included in this metric."
            )

            kpi20.metric(
                label="Snipes percent",
                value=f"{round(snipes_percent, 2)}%",
                help="Snipes are transactions with a very high gas price. They are usually frontrunners or bots trying "
                     "to buy the token ASAP, just after the launch to book a low price."
            )

            kpi30.metric(
                label="Average buy order size",
                value=f"{round(avg_trade_size, 3)} ETH"
            )

            kpi40.metric(
                label="Average trade result",
                value=f"{round(avg_trade_result, 3)} ETH",
                help="How big is the average result of a trade. Only for tokens that have both buy&sell transactions. "
                     "Values are positive for profitable wallets."
            )

            st.markdown("### In/out transactions")
            kpi11, kpi21, kpi31, kpi41 = st.columns(4)

            kpi11.metric(
                label="ETH in (tx+internal)",
                value=f"{round(total_eth_in, 3)} ETH",
                delta=f"+ {round(total_eth_internal_in, 3)} ETH internal",
                help="Internal transactions are counted separately to avoid double counting"
            )

            kpi21.metric(
                label="ETH out",
                value=f"{round(total_eth_out, 3)} ETH"
            )

            kpi31.metric(
                label="Stablecoins in",
                value=f"{round(total_stablecoins_in, 2)} $",
                help="Total value of stablecoins that were sent to the wallet. Stablecoins are tokens with "
                     "a value of 1$."
            )

            kpi41.metric(
                label="Stablecoins out",
                value=f"{round(total_stablecoins_out, 2)} $"
            )

            st.markdown("### Trading metrics")
            kpi12, kpi22, kpi32, kpi42 = st.columns(4)

            kpi12.metric(
                label="Total buys value (excl. snipes and tokens flow)",
                value=f"{round(total_eth_buy, 3)} ETH",
                delta=f"{round(total_eth_sell - total_eth_buy, 3)} ETH trading result",
                help="Trading result is the difference between total sells and total buys. Tokens that have at least 1 "
                     "snipe or in/out transaction are not included in this metric."
            )

            kpi22.metric(
                label="Total sells value (excl. snipes and tokens flow)",
                value=f"{round(total_eth_sell, 3)} ETH"
            )

            kpi32.metric(
                label="Token txs in",
                value=f"{round(count_tokens_in, 0)}",
                help="Number of transactions where the wallet is the recipient of the token"
            )

            kpi42.metric(
                label="Token txs out",
                value=f"{round(count_tokens_out, 0)}"
            )

            st.divider()

            # Create two columns for charts
            fig_col10, fig_col20 = st.columns(2)
            with fig_col10:
                st.markdown("### Cumulative trading result by trade", help="This chart shows the cumulative trading "
                                                                           "result by trade. It is useful to see the "
                                                                           "evolution of the trading result over time.")
                fig10 = px.line(
                    data_frame=cum_res_df, y=cum_res_df["cumResult"], x=cum_res_df.index
                )
                fig10.add_scatter(y=cum_res_df["cumBuy"], x=cum_res_df.index, mode='lines', fillcolor='green',
                                  name="Buy")
                fig10.add_scatter(y=cum_res_df["cumSell"], x=cum_res_df.index, mode='lines', fillcolor='red',
                                  name="Sell")
                st.write(fig10)

            with fig_col20:
                st.markdown("### Daily trades")
                fig20 = px.bar(data_frame=trades_per_day_df, x="date", y='trades_number',
                               labels={'hash': 'number of trades'},)
                st.write(fig20)

            st.markdown("### Transactions detailed view", help="All the transactions for the wallet.")
            st.dataframe(transactions_df)

            histogram_col, pie_chart_col = st.columns(2)

            with histogram_col:
                st.markdown("### Histogram")
                histogram_filter = st.selectbox("Select the column", transactions_df.columns.values.tolist(), index=8)

                histogram = px.histogram(transactions_df, x=histogram_filter, title=histogram_filter)
                st.write(histogram)

            with pie_chart_col:
                st.markdown("### Pie chart")
                pie_chart_filter = st.selectbox("Select the column", transactions_df.columns.values.tolist(), index=6)

                pie_chart_values = transactions_df.loc[:, pie_chart_filter].value_counts()

                pie_chart = px.pie(pie_chart_values, values=pie_chart_values.values, names=pie_chart_values.index,
                                   title=pie_chart_filter)
                st.write(pie_chart)

            st.divider()
            st.markdown("### Trades detailed view", help="This table contains all the trades grouped by token "
                                                         "(separately for buy and sell txs). Some of the tokens may "
                                                         "have not been sold yet, so they are not included.")
            st.dataframe(self.token_trades_df)

            def to_csv(df):
                # Convert DataFrame to a CSV string
                output = StringIO()
                df.to_csv(output, index=False)

                # Set the StringIO object to the beginning
                output.seek(0)
                return output.getvalue()

            def create_download_link(df, filename):
                csv = to_csv(df)

                # Encode CSV string
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
                return href

            if st.button('Save trades (table above) to CSV'):
                st.write(f'Saved the data to a file: {self.wallet_address}_trades.csv')

                st.markdown(create_download_link(self.token_trades_df, f"{self.wallet_address}_trades.csv"),
                            unsafe_allow_html=True)

            if st.button('Save all swap txs to CSV'):
                st.write(f'Saved the data to a file: {self.wallet_address}_swap_txs.csv')

                st.markdown(create_download_link(self.swap_txs_df,
                                                 f"{self.wallet_address}_swap_txs.csv"), unsafe_allow_html=True)

            st.markdown("Powered by Etherscan.io APIs")


if __name__ == "__main__":
    dashboard = Dashboard("0x28C79b441c460D33a2751652D8793566860aB666")
    dashboard.main()
