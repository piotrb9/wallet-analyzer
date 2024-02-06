"""Simple traders dashboard with Streamlit"""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from wallet_analyzer_eth import WalletAnalyzer


class Dashboard:
    def __init__(self, wallet_address: str):
        self.tokens_txs_df = None
        self.wallet_analyzer = None
        self.wallet_address = wallet_address

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
        wallet_analyzer.calculate_tokens_txs(drop_snipes=True, drop_in_out_tokens=True)

        self.wallet_analyzer = wallet_analyzer

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
            count_tokens_out = self.wallet_analyzer.calculate_total_values(drop_snipes=True, drop_in_out_tokens=True)

        final_trade_result = self.wallet_analyzer.final_trade_result()
        snipes_percent = self.wallet_analyzer.snipes_percent()
        avg_trade_size = self.wallet_analyzer.avg_trade_size()
        avg_trade_result = self.wallet_analyzer.avg_trade_result()

        # Charts
        trades_per_day_df = self.wallet_analyzer.trades_per_day(True, False, True)
        cum_res_df = self.wallet_analyzer.cumulated_daily_trading_result(True, False, True)

        # Dataframes
        transactions_df = self.wallet_analyzer.txs_df
        transactions_df['dateTime'] = pd.to_datetime(transactions_df.loc[:, 'timeStamp'], unit='s')
        transactions_df = transactions_df.loc[:, ['dateTime', 'hash', 'from', 'to', 'value', 'gasPrice', 'txType',
                                                  'swapType', 'swapEth', 'tokenValue', 'tokenName', 'tokenSymbol',
                                                  'tokenCa', 'snipe', 'txFee']]

        placeholder = st.empty()

        with placeholder.container():
            kpi10, kpi20, kpi30, kpi40 = st.columns(4)

            kpi10.metric(
                label="Final trade result (only buy+sell txs)",
                value=f"{round(final_trade_result, 3)} ETH"
            )

            kpi20.metric(
                label="Snipes percent",
                value=f"{round(snipes_percent, 2)}%",
            )

            kpi30.metric(
                label="Average buy order size",
                value=f"{round(avg_trade_size, 3)} ETH"
            )

            kpi40.metric(
                label="Average trade result",
                value=f"{round(avg_trade_result, 3)} ETH"
            )

            st.markdown("### In/out transactions")
            kpi11, kpi21, kpi31, kpi41 = st.columns(4)

            kpi11.metric(
                label="ETH in (tx+internal)",
                value=f"{round(total_eth_in, 3)} ETH",
                delta=f"+ {round(total_eth_internal_in, 3)} ETH internal"
            )

            kpi21.metric(
                label="ETH out",
                value=f"{round(total_eth_out, 3)} ETH"
            )

            kpi31.metric(
                label="Stablecoins in",
                value=f"{round(total_stablecoins_in, 2)} $"
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
                delta=f"{round(total_eth_sell - total_eth_buy, 3)} ETH trading result"
            )

            kpi22.metric(
                label="Total sells value (excl. snipes and tokens flow)",
                value=f"{round(total_eth_sell, 3)} ETH"
            )

            kpi32.metric(
                label="Token txs in",
                value=f"{round(count_tokens_in, 0)}"
            )

            kpi42.metric(
                label="Token txs out",
                value=f"{round(count_tokens_out, 0)}"
            )

            st.divider()

            # Create two columns for charts
            fig_col10, fig_col20 = st.columns(2)
            with fig_col10:
                st.markdown("### Cumulative trading result by trade")
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
                # print(trades_per_day_df)
                fig20 = px.bar(data_frame=trades_per_day_df, x="date", y='trades_number',
                               labels={'hash': 'number of trades'},)
                st.write(fig20)

            st.markdown("### Transactions detailed view")
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
            st.markdown("### Trades detailed view")
            st.dataframe(self.wallet_analyzer.token_trades)

            current_location = os.path.dirname(os.path.realpath(__file__))
            save_files_location = os.path.join(current_location, "saved_files")

            if st.button('Save trades (table above) to CSV'):
                self.wallet_analyzer.token_trades.to_csv(os.path.join(save_files_location,
                                                                      f"{self.wallet_address}_trades.csv"))

                st.write(f'Saved the data to a file: {self.wallet_address}_trades.csv')

            if st.button('Save all swap txs to CSV'):
                self.wallet_analyzer.get_swap_txs().to_csv(os.path.join(save_files_location,
                                                                        f"{self.wallet_address}_swap_txs.csv"),
                                                           index=False)

                st.write(f'Saved the data to a file: {self.wallet_address}_swap_txs.csv')


if __name__ == "__main__":
    dashboard = Dashboard("0x7e5e597c3005037246f9efdb61f79d193d1d546c")
    dashboard.main()
