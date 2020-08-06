package com.xapi.client;

import java.util.HashMap;

import pro.xstore.api.message.command.APICommandFactory;
import pro.xstore.api.message.records.STickRecord;
import pro.xstore.api.message.response.LoginResponse;
import pro.xstore.api.message.response.SymbolResponse;
import pro.xstore.api.streaming.StreamingListener;
import pro.xstore.api.sync.Credentials;
import pro.xstore.api.sync.ServerData.ServerEnum;
import pro.xstore.api.sync.SyncAPIConnector;

import com.xapi.utilities.TestStreamingListener;
import com.xapi.utilities.TestStreamingListener2;

public class FirstTestClient {

	//private static Singleton singleton = new Singleton( );
	private static SyncAPIConnector connector;
	static SymbolResponse symbolResponse;
	static LoginResponse loginResponse;
	static Credentials credentials;
	//static String symbol = "EURCHF";
	static HashMap<String, Integer> tradeCount = new HashMap<String, Integer>();
	/*public static final float LOT_SIZE = 2f;
	public static final float PIP_SIZE = 0.0001f;
    public static final float PIP_SIZE_JPY = 0.01f;*/
	static int count = 0;
	
	
	
	/*static LoginResponse getLoginResponse(){
		
		if (loginResponse == null)
			try {
				loginResponse = APICommandFactory
						.executeLoginCommand(connector, // APIConnector
								getCredentials());
			}  catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		return loginResponse;
		
	}*/
	public static void main(String[] args) {
		/* args[0]  Symbol
		 * args[1] EMA8
		 * args[2] EMA20
		 * args[3] EMA50
		 * args[4] MAYBE to keep the current Open
		 */

		try {

			// Create new connector
			connector = new SyncAPIConnector(ServerEnum.REAL);

			// Create new credentials
			// TODO: Insert your credentials
			 credentials = new Credentials("xxx", "xxx");

			// Create and execute new login command
			 loginResponse = APICommandFactory
					.executeLoginCommand(connector, // APIConnector
							credentials // Credentials
					);

			// Check if user logged in correctly
			if (loginResponse.getStatus() == true) {
				
				//OK: Limit Order tester
				//TestStreamingListener2.limitTradeInitiator(connector,"EURUSD", 1.12, "Buy", 1.11, 1.13);
				
				
				
				// Print the message on console
				System.out.println("User logged in");

				StreamingListener strListener = new TestStreamingListener2(
						args[0], args[1], args[2], args[3], args[4],
						connector);
				// strListener.receiveTickRecord(tickRecord)

				connector.connectStream(strListener);
				//connector.subscribePrice(args[0], 1000);
			    connector.subscribePrice(args[0]);
				// connector.subscribeCandles(Arrays.asList(args));
				connector.subscribeCandle(args[0]);
				connector.subscribeTrades();
				//connector.subscribeProfits();

				symbolResponse = APICommandFactory.executeSymbolCommand(
						connector, args[0]);
				
				// System.out.println(symbolResponse.getReturnData());

				System.out.println(args[0] + " Initial symbol price: "
						+ symbolResponse.getSymbol().getAsk());
						

			} else {

				// Print the error on console
				System.err.println("Error: user couldn't log in!");

			}

			// Close connection
			// connector.close();
			// System.out.println("Connection closed");

			// Catch errors
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	static void Streaming_TickRecordReceived(STickRecord tickRecord) {
		// if (tickRecord.getLevel() == 0)
		System.out.println("Current price: " + tickRecord.getAsk());
	}

	/*public static void tradeInitiator(String symbol, double limitprice, String buysell,
			double stopLoss, double strategy)
			

	{
		// Opening a trade

		double price = 0.0;
		double sl = 0.0;
		double tp = 0.0;
		double volume = LOT_SIZE;
		long order = 0;
		long expiration = 0;
		TRADE_OPERATION_CODE tradeCode = null;
		TradeTransactionResponse tradeTransactionResponse;
		TradeTransactionStatusResponse ttsResponse = null;
		SymbolResponse symbolResponse1 = null;

		try {
			LoginResponse ls1 = getLoginResponse();
			if (ls1.getStatus())
			 symbolResponse1 = APICommandFactory
					.executeSymbolCommand(getConnector(), symbol);
			if (buysell.equals("Buy")) {
				tradeCode = TRADE_OPERATION_CODE.BUY;
				price = symbolResponse1.getSymbol().getAsk();
				stopLoss = Math.max(Math.min(stopLoss, symbolResponse1
						.getSymbol().getBid()) - (symbol.endsWith("JPY")?3*PIP_SIZE_JPY:3*PIP_SIZE), symbolResponse1.getSymbol().getBid() 
						- (symbol.endsWith("JPY")?5*PIP_SIZE_JPY:5*PIP_SIZE)); // Max SL of 5 pips
															// below the Bid
				tp = price + (price - stopLoss) * 1.5; // Conservative TP to
														// begin with with
														// Risk/Reward at 1:1
			} else if (buysell.equals("Sell")) {
				tradeCode = TRADE_OPERATION_CODE.SELL;
				price = symbolResponse1.getSymbol().getBid();
				stopLoss = Math.min(Math.max(stopLoss, symbolResponse1
						.getSymbol().getAsk()) + (symbol.endsWith("JPY")?3*PIP_SIZE_JPY:3*PIP_SIZE), symbolResponse1.getSymbol().getAsk() 
						+ (symbol.endsWith("JPY")?5*PIP_SIZE_JPY:5*PIP_SIZE)); // // Max SL of 5 pips
															// above the Ask
				tp = price - (stopLoss - price) * 1.5; // Conservative TP to
														// begin with with
														// Risk/Reward at 1:1
			}

			System.out.println(symbol + " Strategy: " + strategy
					+ " Request for Opening trade !!!" + buysell + " SL :"
					+ stopLoss + " Price :" + price + " Bid/Ask :"
					+ symbolResponse1.getSymbol().getBid() + "/"
					+ symbolResponse1.getSymbol().getAsk());

			// if (tradeCount == 0 )
			// {
			TradeTransInfoRecord ttOpenInfoRecord = new TradeTransInfoRecord(
					tradeCode, TRADE_TRANSACTION_TYPE.OPEN,
					(buysell.equals("Buy")?(limitprice >= symbolResponse1.getSymbol().getAsk()?
							symbolResponse1.getSymbol().getAsk():limitprice):
								(limitprice <= symbolResponse1.getSymbol().getBid()?
										symbolResponse1.getSymbol().getBid():limitprice)
							),
					stopLoss, tp, symbol, volume, order,
					"Strategy:" + strategy, expiration);

			// try {
			tradeTransactionResponse = APICommandFactory
					.executeTradeTransactionCommand(getConnector(), ttOpenInfoRecord);
			ttsResponse = APICommandFactory
					.executeTradeTransactionStatusCommand(getConnector(),
							tradeTransactionResponse.getOrder());
			count++;
		
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {
			System.out.println("Trade Transaction status" + ttsResponse);
			symbolResponse1 = null;
		}
	}
	
	public static void tradeModifier(String symbol,int cmd, long orderID, long positionID,double price,
			double stopLoss, double takeprofit){
		
		double volume = LOT_SIZE;
		long expiration = 0;
		//double price = 0.0;
		SymbolResponse symbolResponse2 = null;
		TradeTransactionResponse tradeTransactionResponse;
		TradeTransactionStatusResponse ttsResponse = null;
		System.out.println(symbol + " Request received to Modify trade#, SL, TP " + orderID + "::"+ stopLoss + "::"+ takeprofit);
		
		
		try {
			LoginResponse ls2 = getLoginResponse();
			if (ls2.getStatus())
			 symbolResponse2 = APICommandFactory
						.executeSymbolCommand(getConnector(), symbol);
			 
			 TradeTransInfoRecord ttOpenInfoRecord = new TradeTransInfoRecord(
						cmd==0 || cmd==2?TRADE_OPERATION_CODE.BUY:TRADE_OPERATION_CODE.SELL, TRADE_TRANSACTION_TYPE.MODIFY,
						cmd==0?symbolResponse2.getSymbol().getAsk():symbolResponse2.getSymbol().getBid(),
						stopLoss, takeprofit, symbol, volume, positionID,
						"Modified", expiration);
			tradeTransactionResponse = APICommandFactory
					.executeTradeTransactionCommand(getConnector(), ttOpenInfoRecord);
			ttsResponse = APICommandFactory
					.executeTradeTransactionStatusCommand(getConnector(),
							tradeTransactionResponse.getOrder());
		} catch (APICommandConstructionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (APIReplyParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (APICommunicationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (APIErrorResponse e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		finally{
			
			System.out.println(symbol + " TRade Modification status "+ ttsResponse);
		}
		
	}
			*/
	
	
}


