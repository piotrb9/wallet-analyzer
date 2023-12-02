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

        # Data
        self.get_wallet_data(self.wallet_address)
        total_eth_in, total_eth_internal_in, total_eth_out, total_eth_buy, total_eth_sell, total_stablecoins_in,\
            total_stablecoins_out, total_fees_eth, count_tokens_in,\
            count_tokens_out = self.wallet_analyzer.calculate_total_values(drop_snipes=True, drop_in_out_tokens=True)

        final_trade_result = self.wallet_analyzer.final_trade_result()
        snipes_percent = self.wallet_analyzer.snipes_percent()
        avg_trade_size = self.wallet_analyzer.avg_trade_size()
        avg_trade_result = self.wallet_analyzer.avg_trade_result()

        transactions_df = self.wallet_analyzer.txs_df
        transactions_df['dateTime'] = pd.to_datetime(transactions_df.loc[:, 'timeStamp'], unit='s')

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


if __name__ == "__main__":
    dashboard = Dashboard("0x7e5e597c3005037246f9efdb61f79d193d1d546c")
    dashboard.main()
