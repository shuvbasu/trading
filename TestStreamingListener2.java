package com.xapi.utilities;

import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import pro.xstore.api.message.codes.TRADE_OPERATION_CODE;
import pro.xstore.api.message.codes.TRADE_TRANSACTION_TYPE;
import pro.xstore.api.message.command.APICommandFactory;
import pro.xstore.api.message.records.SBalanceRecord;
import pro.xstore.api.message.records.SCandleRecord;
import pro.xstore.api.message.records.SKeepAliveRecord;
import pro.xstore.api.message.records.SNewsRecord;
import pro.xstore.api.message.records.SProfitRecord;
import pro.xstore.api.message.records.STickRecord;
import pro.xstore.api.message.records.STradeRecord;
import pro.xstore.api.message.records.STradeStatusRecord;
import pro.xstore.api.message.records.TradeTransInfoRecord;
import pro.xstore.api.message.response.TradeTransactionResponse;
import pro.xstore.api.message.response.TradeTransactionStatusResponse;
import pro.xstore.api.streaming.StreamingListener;
import pro.xstore.api.sync.Connector;
import pro.xstore.api.sync.ServerData.ServerEnum;
import pro.xstore.api.sync.SyncAPIConnector;

public class TestStreamingListener2 extends StreamingListener {

	private static SyncAPIConnector connector;
	private static String symbol;
	private static final double MAX_CANDLE_SIZE = 100;
	private static final double MAX_CANDLE_SIZE_JPY = 50;
	private static final double MIN_CANDLE_SIZE = 10;
	private static final double LOT_SIZE = 1.0;
	private static final double PIP_SIZE = 0.0001;
	private static final double PIP_SIZE_JPY = 0.01;
	//private static HashMap<String, ArrayList<SCandleRecord>> last3Candles = new HashMap<>();
	private static HashMap<String, Double[]> runningBidAsk = new HashMap<>();
	//private static HashMap<String, Double[]> lastCandleHighLow30M = new HashMap<>();
	private static HashMap<String, Double[]> lastCandleHighLow1H = new HashMap<>();
	// Trading hours
	private static HashMap<String, Double[]> tradingHours = new HashMap<>();
	//private static HashMap<String, ArrayList<Double>> open15M = new HashMap<>();
	private static HashMap<String, ArrayList<Double>> close15M = new HashMap<>();
	/*private static HashMap<String, ArrayList<Double>> open30M = new HashMap<>();
	private static HashMap<String, Long> modifiedFlag = new HashMap<>();
	
	// Usage: Symbol: [1(Buy)/2(Sell),Stoploss]
	private static HashMap<String, Double[]> tradeOpenSignal = new HashMap<>();*/
	// Candle Records
	static ArrayList<SCandleRecord> sc = new ArrayList<SCandleRecord>();
	static long candleCounter1M = 0;
	// EMA records
	static ArrayList<Float> ema = new ArrayList<Float>();
	static double ema10 = 0.0;

	private static String USER_NAME = "Autotrading2017";  // GMail user name (just the part before "@gmail.com")
    private static String PASSWORD = "Trading2017$"; // GMail password
    private static String[] RECIPIENT = {"sbasu81@gmail.com"};
	// 5M startup values, try with different parameters , Ex: 8,12,7 for 5M
	// chart
	static double start1Hema50 = 0.0, start1Hema8 = 0.0, start1Hema20 = 0.0,
			start5Msignalema9 = 0.0, prev1Hemadiff = 99999.9, curr1HOpen = 0.0;

	// Previous MACDs

	static double prev30Mmacd = 99999.0, prev1Hmacd = 99999.0,
			prev1Hmacd_1 = 99999.0;

	static Map<String, Integer> candleCounter = new HashMap<String, Integer>();

	// Maps for storing multiple symbols
	// Key: Symbol, Values: List of EMAs

	public TestStreamingListener2(String symbols, String fast5m, String slow5m,
			String slowest, String open1H_1, SyncAPIConnector conn) {
		// Assign the EMAs from Client here in this constructor
		symbol = symbols;
		start1Hema8 = Double.parseDouble(fast5m);
		start1Hema20 = Double.parseDouble(slow5m);
		start1Hema50 = Double.parseDouble(slowest);
		curr1HOpen = Double.parseDouble(open1H_1);
		// Calculate the last EMA diff
		prev1Hemadiff = start1Hema8 - start1Hema20;
		// prev1Hmacd_1 = Double.parseDouble(open1H_1);
		// start5Mema10 = Double.parseDouble(ema105m);
		// start5Mema20 = Double.parseDouble(ema205m);
		connector = conn;
		// credentials = cr;
		// loginResponse = lres;
		// Initialize trading hours
		tradingHours.put("USD", new Double[] { 13.00, 21.00 });
		tradingHours.put("GBP", new Double[] { 08.00, 16.00 });
		tradingHours.put("JPY", new Double[] { 00.00, 07.00 });
		tradingHours.put("EUR", new Double[] { 07.00, 16.00 });
		tradingHours.put("AUD", new Double[] { 00.00, 07.00 });
		tradingHours.put("NZD", new Double[] { 00.00, 07.00 });
		tradingHours.put("CAD", new Double[] { 13.00, 21.00 });
	}

	static SyncAPIConnector getConnector() throws Exception {
		if (connector == null)
			connector = new SyncAPIConnector(ServerEnum.DEMO);
		return connector;
	}

	@SuppressWarnings("rawtypes")
	static Map<String, ArrayList> masterEMAMap = new HashMap<String, ArrayList>();

	static final long systemInitializationTS = System.currentTimeMillis();
	static DecimalFormat df = new DecimalFormat("##.#####");

	// No. of trades
	static Map<String, Integer> tradeCount = new HashMap<String, Integer>();

	// static double[] starting5mEMA = {1.54693,1.54696,1.54799};
	// static double start5mema = 1.55792;

	@Override
	public void receiveTradeRecord(STradeRecord tradeRecord) {
		// TODO Auto-generated method stub

		/*if (tradeRecord.getSymbol().equals(symbol)) {

			System.out.println("Keeping an eye on trade: "
					+ tradeRecord.toString());
			if (tradeRecord.isClosed()
					|| tradeRecord.getState().equalsIgnoreCase("Deleted"))
				tradeCount.put(tradeRecord.getSymbol(), 0);
			else
				tradeCount.put(tradeRecord.getSymbol(), 1);
		}*/

		// Keeping track of running profit
		/*
		 * if (tradeCount.get(tradeRecord.getSymbol()) != null ||
		 * tradeCount.get(tradeRecord.getSymbol()) != 0) { double nextTP = 0.0;
		 * double nextSL = 0.0; double currentPrice = 0.0; if
		 * (runningBidAsk.get(tradeRecord.getSymbol()) != null) { if
		 * (tradeRecord.getCmd() == 0 || tradeRecord.getCmd() == 2) { //Modify
		 * Buy Order currentPrice =
		 * runningBidAsk.get(tradeRecord.getSymbol())[0]; // If Current Bid
		 * price exceeds 0.85 times of TP, Move the SL & adjust the TP if
		 * ((currentPrice - tradeRecord.getOpen_price()) > 0.9 *
		 * (tradeRecord.getTp() - tradeRecord.getOpen_price())) { //MODIFY the
		 * Order, adjust SL & TP
		 * //System.out.println("Current SL, TP within Modify block for Order --> "
		 * + tradeRecord.getOrder()+ ":" + tradeRecord.getSl() + ":"+
		 * tradeRecord.getTp() ) ; //nextSL = currentPrice -
		 * (tradeRecord.getSymbol
		 * ().endsWith("JPY")?3*FirstTestClient.PIP_SIZE_JPY
		 * :3*FirstTestClient.PIP_SIZE); nextSL = tradeRecord.getOpen_price();
		 * nextTP = currentPrice +
		 * (tradeRecord.getSymbol().endsWith("JPY")?6*FirstTestClient
		 * .PIP_SIZE_JPY:6*FirstTestClient.PIP_SIZE);
		 * 
		 * FirstTestClient
		 * .tradeModifier(tradeRecord.getSymbol(),tradeRecord.getCmd
		 * (),tradeRecord
		 * .getOrder(),tradeRecord.getPosition(),currentPrice,nextSL,nextTP);
		 * 
		 * }
		 * 
		 * } else if (tradeRecord.getCmd() == 1 || tradeRecord.getCmd() == 3){
		 * 
		 * //Modify Sell Order currentPrice =
		 * runningBidAsk.get(tradeRecord.getSymbol())[1];
		 * //System.out.println("Current SL, TP within Modify block for Order --> "
		 * + tradeRecord.getOrder()+ ":" + tradeRecord.getSl() + ":"+
		 * tradeRecord.getTp() ) ;
		 * 
		 * // If Current Bid price exceeds 0.85 times of TP, Move the SL &
		 * adjust the TP if (Math.abs((currentPrice -
		 * tradeRecord.getOpen_price())) > 0.8 * Math.abs((tradeRecord.getTp() -
		 * tradeRecord.getOpen_price()))) { //MODIFY the Order, adjust SL & TP
		 * System
		 * .out.println("Current SL, TP within Modify block for Order --> "+
		 * tradeRecord.getOrder()+ ":" + tradeRecord.getSl() + ":"+
		 * tradeRecord.getTp() ) ; nextSL = currentPrice +
		 * (tradeRecord.getSymbol
		 * ().endsWith("JPY")?3*FirstTestClient.PIP_SIZE_JPY
		 * :3*FirstTestClient.PIP_SIZE); nextTP = currentPrice -
		 * (tradeRecord.getSymbol
		 * ().endsWith("JPY")?6*FirstTestClient.PIP_SIZE_JPY
		 * :6*FirstTestClient.PIP_SIZE);
		 * 
		 * FirstTestClient
		 * .tradeModifier(tradeRecord.getSymbol(),tradeRecord.getCmd
		 * (),tradeRecord
		 * .getOrder(),tradeRecord.getPosition(),currentPrice,nextSL,nextTP);
		 * 
		 * }
		 * 
		 * } }
		 */
	}

	@Override
	public void receiveTickRecord(STickRecord tickRecord) {
		// Store the current running Bid/Ask to be used for profit management
		// above
		runningBidAsk.put(tickRecord.getSymbol(),
				new Double[] { tickRecord.getBid(), tickRecord.getAsk() });

	}

	@Override
	public void receiveBalanceRecord(SBalanceRecord balanceRecord) {
		// TODO Auto-generated method stub

	}

	@Override
	public void receiveNewsRecord(SNewsRecord newsRecord) {
		// TODO Auto-generated method stub

	}

	@Override
	public void receiveTradeStatusRecord(STradeStatusRecord tradeStatusRecord) {
		// TODO Auto-generated method stub
		System.out.println("Keeping an eye on tradeStatus: "
				+ tradeStatusRecord.toString());

	}

	@Override
	public void receiveProfitRecord(SProfitRecord profitRecord) {
		// TODO Auto-generated method stub
		// System.out.println("Checking ticking Profit/Loss..Order --> " +
		// profitRecord + " : Profit -->" + profitRecord.getProfit());
		// Close the trade if Profit/Loss exceeds 50 GBP (To Start with)

	}

	@Override
	public void receiveKeepAliveRecord(SKeepAliveRecord keepAliveRecord) {
		// TODO Auto-generated method stub

	}

	@Override
	public void receiveCandleRecord(SCandleRecord candleRecord) {
		// TODO Auto-generated method stub
		// double MACD1Mdivergence = 0.0, MACD15Mdivergence = 0.0;
		double[] MACD5Mdivergence = { 0.0, 0.0 };
		// boolean candle30M = false;

		candleCounter1M++;
		if (candleCounter.get(candleRecord.getSymbol()) == null)
			candleCounter.put(candleRecord.getSymbol(), 1);
		else
			candleCounter
					.put(candleRecord.getSymbol(), (Integer) (candleCounter
							.get(candleRecord.getSymbol())) + 1);

		// Store the running high/low of candles

		if (candleCounter.get(candleRecord.getSymbol()) > 1) {

			if (lastCandleHighLow1H.get(candleRecord.getSymbol()) != null) {
				double high = lastCandleHighLow1H.get(candleRecord.getSymbol())[0];
				double low = lastCandleHighLow1H.get(candleRecord.getSymbol())[1];
				if (candleRecord.getHigh() > high)
					high = candleRecord.getHigh();
				if (candleRecord.getLow() < low)
					low = candleRecord.getLow();
				lastCandleHighLow1H.put(candleRecord.getSymbol(), new Double[] {
						high, low });

			} else
				lastCandleHighLow1H.put(candleRecord.getSymbol(), new Double[] {
						0.0, 100000.0 });

			// Now store the Open for 15 & 30 M candles

			/*
			 * if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 30 == 1)
			 * open15M.put(candleRecord.getSymbol(), candleRecord.getOpen());
			 * 
			 * if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 60 == 1)
			 * open30M.put(candleRecord.getSymbol(), candleRecord.getOpen());
			 */

		}

		// long currTS = System.currentTimeMillis();
		// Ping every 10 mins
		if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 10 == 0) {
			try {
				APICommandFactory.executePingCommand(getConnector());

				System.out.println("Login Renewed...!!");
			} catch (Exception e) {
				// TODO Auto-generated catch block
				System.out.println("Ping failed...!!");
				e.printStackTrace();
			}finally {
				if((candleCounter.get(candleRecord.getSymbol()) - 1) % 120 == 0) {
					
					EmailUtility.sendFromGMail(USER_NAME, PASSWORD,RECIPIENT, "2H HEARTBEAT!! " + symbol , symbol 
							+ " pinging live:: "+ candleRecord.toString());
				}
			}
		}

		/*// Keep the 15M close when running on 1H candles
		if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 15 == 0) {

			List<Double> a15MList = null;
			if (close15M.get(candleRecord.getSymbol()) == null) {
				a15MList = new ArrayList<Double>();
				a15MList.add(candleRecord.getClose());
			}

			close15M.put(candleRecord.getSymbol(), (ArrayList<Double>) a15MList);

		}*/

		// Add the Open candle
		if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 60 == 1)
			sc.add(candleRecord);
		if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 60 == 0)

		{

			double high15M = 99999.0;
			double low15M = 0.0;
			if (candleCounter1M >= 60) {
				high15M = lastCandleHighLow1H.get(candleRecord.getSymbol())[0];
				low15M = lastCandleHighLow1H.get(candleRecord.getSymbol())[1];
			}
			System.out.println("Checking ticking candles..la la la."
					+ candleRecord.toString());
			sc.add(candleRecord);

			// if(sc.size() >= 2)
			MACD5Mdivergence = EMACrossover.getEMACrossOver(candleRecord
					.getSymbol(), candleRecord.getClose(), sc.size() >= 2 ? sc
					.get(sc.size() - 2).getOpen() : curr1HOpen, start1Hema8,
					start1Hema20, start1Hema50, (sc.size() % 4 == 0));

			// String candleTrend = checkTrend(candleRecord);
			System.out.println(candleRecord.getSymbol()
					+ " In TestStreaming..MACD : "
					+ df.format(MACD5Mdivergence[0]));

			// If MACD algo returns +ve && (IMP) we have a Green candle &&
			// Candle size within MAX limit, then BUY

			// TODO
			// Shadow check, initiate if candle body > 60% of size
			// SL for M30 should be based of last 2 candles
			// Check MAX candle size for JPY, could be 30 i.e half of EUR*
			// candles
			// Check Min size of candle, set at 5 pips
			// Check if there's a same trade b4 in M15 b4 initiating a M30 trade
			// (Optional)
			// Think of making Limit Orders (+/- 2 pips of candle close) instead
			// of Market order in order to limit the surge during news break
			// Implement a 30 min no trade window before & after news break
			// Implement trading hoursc

			if (MACD5Mdivergence[0] != 0.0) {
				System.out
						.println("EMA signal received !! 1H Candle High/Low, Close, Open "
								+ high15M + "::" + low15M + "::" + candleRecord.getClose() + "::"+ sc.get(sc.size() - 2)
								.getOpen());

				// Check trading hours range
				//if (checkTradinghours(candleRecord.getSymbol())) {
					if ((Math.abs(high15M - low15M) < (candleRecord.getSymbol()
							.endsWith("JPY") ? MAX_CANDLE_SIZE_JPY
							* PIP_SIZE_JPY : MAX_CANDLE_SIZE * PIP_SIZE))
							&& (Math.abs(high15M - low15M) > (candleRecord
									.getSymbol().endsWith("JPY") ? MIN_CANDLE_SIZE
									* PIP_SIZE_JPY
									: MIN_CANDLE_SIZE * PIP_SIZE))) {
						// TODO:
						// For 30M candle, relax the criteria to (Close > 1/2
						// (Prev Close - Prev Open) rather than strictly upward
						if (MACD5Mdivergence[0] > 0.0
						// && (candleRecord.getClose() >
						// (sc.get(sc.size() - 4).getOpen() + 0.5 *
						// Math.abs((sc.get(sc.size() - 3).getClose())
						// - sc.get(sc.size() - 4).getOpen()))
								&& // Check upward shadow
								((high15M - candleRecord.getClose()) <= (candleRecord
										.getClose() - low15M)) // Check last
																	// half , if
																	// its
																	// bullish
																	// OR if
																	// bearish
																	// check if
																	// last half
																	// candle is
																	// not
																	// crossing
																	// half of
																	// 1H candle
							/*	&& ((candleRecord.getClose() >= close15M
										.get(candleRecord.getSymbol()).get(1) || Math
										.abs((close15M.get(
												candleRecord.getSymbol())
												.get(1) - candleRecord.getClose())) < Math
										.abs((candleRecord.getClose() - sc.get(sc.size() - 2)
												.getOpen()) / 2)
								// &&
*/								// close15M.get(candleRecord.getSymbol()).get(3)
								// >
								// close15M.get(candleRecord.getSymbol()).get(2))
								)

						{
							// All positive, initiate a Buy Order
							// Putting stop loss as the low of the 2nd last
							// candle
							System.out.println(candleRecord.getSymbol()
									+ " All +ve..initiate a Buy order");

							// if (tradeCount.get(candleRecord.getSymbol()) ==
							// null || tradeCount.get(candleRecord.getSymbol())
							// == 0)
							// {
							// Set the tradeSignal map to be invoked by
							// tickRecord above
							// tradeOpenSignal.put(candleRecord.getSymbol(), new
							// Double[]{1.0,sc.get((sc.size() - 2) >=
							// 0?(sc.size() - 2):0)
							// .getLow()});
							/*
							 * FirstTestClient
							 * .tradeInitiator(candleRecord.getSymbol
							 * (),runningBidAsk
							 * .get(candleRecord.getSymbol())[1],"Buy",
							 * sc.get((sc.size() - 2) >= 0?(sc.size() - 2):0)
							 * .getLow(),MACD5Mdivergence[1]);
							 */
							// ****IMP: Set SL to MIN of (Low of current 30M
							// candle , slow EMA received from
							// MACDCalculator)****//
							//limitTradeInitiator(candleRecord.getSymbol(),
								//	candleRecord.getClose(), "Buy", low15M, MACD5Mdivergence[2]);

							// }
							// else
							// System.out.println(candleRecord.getSymbol() +
							// " Sorry ! Already an active trade in the system ");
						}

						else if (
						// EMA10Level.equals("Below10EMA")
						// &&
						// If MACD algo returns -ve && (IMP) we have a Red
						// candle , then BUY
						MACD5Mdivergence[0] < 0.0
						// && (candleRecord.getClose() <
						// (sc.get(sc.size() - 4).getOpen() - 0.5 *
						// Math.abs((sc.get(sc.size() - 3).getClose())
						// - sc.get(sc.size() - 4).getOpen()))
								&& // Check downward shadow
								((high15M - candleRecord.getClose()) >= (candleRecord
										.getClose() - low15M))

								 // //Check last half , if its bearish OR if
									// bullish check if last half candle is not
									// crossing half of 1H candle
								//COMMENTED FOR NOW, UNTIL SUFFICIENT MERITS FOUND
								/*&& ((candleRecord
										.getClose() <= close15M
										.get(candleRecord.getSymbol()).get(1) || Math
										.abs((close15M.get(
												candleRecord.getSymbol())
												.get(1) - candleRecord
												.getClose())) < Math
										.abs((close15M.get(
												candleRecord.getSymbol())
												.get(3) - sc.get(sc.size() - 2)
												.getOpen()) / 2)*/
								// &&
								// close15M.get(candleRecord.getSymbol()).get(3)
								// <
								// close15M.get(candleRecord.getSymbol()).get(2)))
								) {
							// All negative, initiate Sell
							System.out.println(candleRecord.getSymbol()
									+ " All -ve..initiate a Sell order");

							// if (tradeCount.get(candleRecord.getSymbol()) ==
							// null || tradeCount.get(candleRecord.getSymbol())
							// == 0)
							// {
							// Set the tradeSignal map to be invoked by
							// tickRecord above
							// tradeOpenSignal.put(candleRecord.getSymbol(), new
							// Double[]{2.0,sc.get((sc.size() - 2) >=
							// 0?(sc.size() - 2):0)
							// .getHigh()});
							// ****IMP: Set SL to MAX of (Low of current 30M
							// candle , slow EMA received from
							// MACDCalculator)****//
							//limitTradeInitiator(candleRecord.getSymbol(),
								//	candleRecord.getClose(), "Sell", high15M,MACD5Mdivergence[2]);

							/*
							 * } else
							 * System.out.println(candleRecord.getSymbol() +
							 * " Sorry ! Already an active trade in the system "
							 * );
							 */
						}
					}
				}
				else
					System.out
							.println("NO EMA CROSSOVER SIGNAL RECEIVED !!");
			} 

			// Reset the High/Low after two 15M candles i.e 30 mins
			// if ((candleCounter.get(candleRecord.getSymbol()) - 1) % 60 == 0)
			lastCandleHighLow1H.put(candleRecord.getSymbol(), new Double[] {
					0.0, 10000.0 });
			/*
			 * } catch (APICommandConstructionException | APIReplyParseException
			 * | APIErrorResponse | APICommunicationException e) { // TODO
			 * Auto-generated catch block e.printStackTrace();
			 * 
			 * }
			 */
			// Reset the 15M close candles
			close15M.put(candleRecord.getSymbol(), null);

		}
		// }

	

	static private void tradeInitiator(String symbol, double price,
			String buySell, double sl, double takeProfit) {

		TRADE_OPERATION_CODE tradeCode = null;
		double stopLoss = 0.0;
		double tp = 0.0;
		long expiration = 0;
		long order = 0;
		TradeTransactionResponse tradeTransactionResponse = null;
		TradeTransactionStatusResponse ttsResponse = null;

		if (buySell.equals("Buy")) {
			tradeCode = TRADE_OPERATION_CODE.BUY;
			// price = symbolResponse1.getSymbol().getAsk();
			stopLoss = Math
					.max(Math.min(
							sl
									- (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									- (symbol.endsWith("JPY") ? 5 * PIP_SIZE_JPY
											: 5 * PIP_SIZE)),
							price
									- (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE)); // Max
																					// SL
																					// of
																					// 5
																					// pips
			// below the Bid
			tp = price + ((price - stopLoss) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		} else if (buySell.equals("Sell")) {
			tradeCode = TRADE_OPERATION_CODE.SELL;
			// price = symbolResponse1.getSymbol().getBid();
			stopLoss = Math
					.min(Math.max(
							sl
									+ (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									+ (symbol.endsWith("JPY") ? 3 * PIP_SIZE_JPY
											: 3 * PIP_SIZE)),
							price
									+ (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE));
			// above the Ask
			tp = price - ((stopLoss - price) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		}

			TradeTransInfoRecord ttOpenInfoRecord = new TradeTransInfoRecord(
				tradeCode, TRADE_TRANSACTION_TYPE.OPEN, price, stopLoss, tp,
				symbol, LOT_SIZE, order, "Strategy:", expiration);

		// try {
		try {

			tradeTransactionResponse = APICommandFactory
					.executeTradeTransactionCommand(getConnector(),
							ttOpenInfoRecord);

			ttsResponse = APICommandFactory
					.executeTradeTransactionStatusCommand(getConnector(),
							tradeTransactionResponse.getOrder());
			tradeCount.put(symbol, 1);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {

			System.out.println(ttsResponse);
		}

	}

	
	public static  void limitTradeInitiator(String symbol, double price,
			String buySell, double sl, double takeProfit) {

		TRADE_OPERATION_CODE tradeCode = null;
		double stopLoss = 0.0;
		double tp = 0.0;
		long expiration = System.currentTimeMillis() + (long)1*60*1000;
		long order = 0;
		TradeTransactionResponse tradeTransactionResponse = null;
		TradeTransactionStatusResponse ttsResponse = null;

		if (buySell.equals("Buy")) {
			tradeCode = TRADE_OPERATION_CODE.BUY_LIMIT;
			// price = symbolResponse1.getSymbol().getAsk();
			stopLoss = Math
					.max(Math.min(
							sl
									- (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									- (symbol.endsWith("JPY") ? 5 * PIP_SIZE_JPY
											: 5 * PIP_SIZE)),
							price
									- (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE)); // Max
																					// SL
																					// of
																					// 5
																					// pips
			// below the Bid
			tp = price + ((price - stopLoss) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		} else if (buySell.equals("Sell")) {
			tradeCode = TRADE_OPERATION_CODE.SELL_LIMIT;
			// price = symbolResponse1.getSymbol().getBid();
			stopLoss = Math
					.min(Math.max(
							sl
									+ (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									+ (symbol.endsWith("JPY") ? 3 * PIP_SIZE_JPY
											: 3 * PIP_SIZE)),
							price
									+ (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE));
			// above the Ask
			tp = price - ((stopLoss - price) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		}

			TradeTransInfoRecord ttOpenInfoRecord = new TradeTransInfoRecord(
				tradeCode, TRADE_TRANSACTION_TYPE.OPEN, price, stopLoss, tp,
				symbol, LOT_SIZE, order, "Strategy:", expiration);

		// try {
			EmailUtility.sendFromGMail(USER_NAME, PASSWORD,RECIPIENT, "TRADE ALERT!! " + symbol + " " + buySell, symbol + " Price:: "+ price + " SL:: "+  stopLoss +
					"TP:: "+ tp);
		try {

			tradeTransactionResponse = APICommandFactory
					.executeTradeTransactionCommand(getConnector(),
							ttOpenInfoRecord);

			ttsResponse = APICommandFactory
					.executeTradeTransactionStatusCommand(getConnector(),
							tradeTransactionResponse.getOrder());
			tradeCount.put(symbol, 1);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {

			System.out.println(ttsResponse);
		}

	}
	public static  void shootEmailTest(String symbol, double price,
			String buySell, double sl, double takeProfit) {

		TRADE_OPERATION_CODE tradeCode = null;
		double stopLoss = 0.0;
		double tp = 0.0;
		long expiration = System.currentTimeMillis() + (long)1*60*1000;
		long order = 0;
		TradeTransactionResponse tradeTransactionResponse = null;
		TradeTransactionStatusResponse ttsResponse = null;

		if (buySell.equals("Buy")) {
			tradeCode = TRADE_OPERATION_CODE.BUY_LIMIT;
			// price = symbolResponse1.getSymbol().getAsk();
			stopLoss = Math
					.max(Math.min(
							sl
									- (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									- (symbol.endsWith("JPY") ? 5 * PIP_SIZE_JPY
											: 5 * PIP_SIZE)),
							price
									- (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE)); // Max
																					// SL
																					// of
																					// 5
																					// pips
			// below the Bid
			tp = price + ((price - stopLoss) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		} else if (buySell.equals("Sell")) {
			tradeCode = TRADE_OPERATION_CODE.SELL_LIMIT;
			// price = symbolResponse1.getSymbol().getBid();
			stopLoss = Math
					.min(Math.max(
							sl
									+ (symbol.endsWith("JPY") ? 2 * PIP_SIZE_JPY
											: 2 * PIP_SIZE),
							price
									+ (symbol.endsWith("JPY") ? 3 * PIP_SIZE_JPY
											: 3 * PIP_SIZE)),
							price
									+ (symbol.endsWith("JPY") ? (MAX_CANDLE_SIZE_JPY - 2)
											* PIP_SIZE_JPY
											: (MAX_CANDLE_SIZE - 2) * PIP_SIZE));
			// above the Ask
			tp = price - ((stopLoss - price) * (takeProfit==2.0?2.0:1.5)); // Conservative TP to
			// begin with with
			// Risk/Reward at 1:1
		}

			TradeTransInfoRecord ttOpenInfoRecord = new TradeTransInfoRecord(
				tradeCode, TRADE_TRANSACTION_TYPE.OPEN, price, stopLoss, tp,
				symbol, LOT_SIZE, order, "Strategy:", expiration);

		// try {
		try {

			tradeTransactionResponse = APICommandFactory
					.executeTradeTransactionCommand(getConnector(),
							ttOpenInfoRecord);

			ttsResponse = APICommandFactory
					.executeTradeTransactionStatusCommand(getConnector(),
							tradeTransactionResponse.getOrder());
			tradeCount.put(symbol, 1);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {

			System.out.println(ttsResponse);
		}

	}

	static boolean checkTradinghours(String symbol) {

		String curr1 = symbol.substring(0, 3);
		String curr2 = symbol.substring(3, 6);
		String hour = new SimpleDateFormat("HH:mm:ss").format(
				new Date(System.currentTimeMillis())).substring(0, 2);
		if (tradingHours.get(curr1) != null) {
			if (Double.parseDouble(hour) >= tradingHours.get(curr1)[0]
					&& Double.parseDouble(hour) <= tradingHours.get(curr1)[1])
				return true;

		} else {
			if (tradingHours.get(curr2) != null) {
				if (Double.parseDouble(hour) >= tradingHours.get(curr2)[0]
						&& Double.parseDouble(hour) <= tradingHours.get(curr2)[1])

					return true;

			}
		}
		return false;
	}

}