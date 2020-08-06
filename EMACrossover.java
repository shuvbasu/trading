package com.xapi.utilities;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class EMACrossover {

	int fastema;
	int slowema;
	int signalema;
	static double EMAYesterdayFast = 0.0, EMAYesterdaySlow = 0.0, EMA4HFAST = 0.0, EMA4HSLOW = 0.0, 
			EMAYesterdaySlowest = 0.0, EMAYesterdaySignal30M = 0.0, MACD30M = 99999.0, MACD_DIFF_30M = 99999.0, EMAYest15MFast = 0.0,
			EMAYest15MSlow = 0.0, EMA10 = 0.0, EMA20 = 0.0,macdVal[],
			PREV_30M_MACD = 99999.0, PREV_1H_MACD_1 = 99999.0;
	static DecimalFormat df = new DecimalFormat("##.#####");
	static Map<String, ArrayList<Double>> macdMap = new HashMap<String, ArrayList<Double>>();
	static Map<String, ArrayList<Double>> macdMap1H = new HashMap<String, ArrayList<Double>>();
	static ArrayList<Double> emaDiff_10_20_list = new ArrayList<Double>();
	static ArrayList<Double> ema4HDiff_list = new ArrayList<Double>();

	EMACrossover(int fema, int sema, int signal) {
		fastema = fema;
		slowema = sema;
		signalema = signal;
	}

	/**
	 * 
	 * 
	 * @param symbol
	 * @param todaysPrice
	 * @param EMAYesFast
	 * @param EMAYestSlow
	 * @param EMAYestSignal
	 * @param EMA15MFast
	 * @param EMA15MSlow
	 * @param EMA15MSignal
	 * @param calc30M
	 * @return double[Macd, StopLoss, Strategy #] 
	 * StopLoss = Slow EMA
	 */
	static synchronized double[] getEMACrossOver(String symbol,
			double todaysPrice, double openPrice, double EMAYesFast, double EMAYestSlow,
			double EMASlowest, boolean calc4H
			) {
		double fema = 0.0, sema = 0.0, signal = 0.0, fema4H = 0.0, sema4H = 0.0, signal30M = 0.0, fema10 = 0.0, sema50 = 0.0;
		double[] emaResult = { 0.0, 1.0, 1.0};

		if (EMAYesterdayFast == 0.0 || EMAYesterdaySlow == 0.0
				|| EMAYesterdaySlowest == 0.0  ) {
			EMAYesterdayFast = EMAYesFast;
			EMAYesterdaySlow = EMAYestSlow;
			EMAYesterdaySlowest = EMASlowest;
			//PREV_1H_MACD = prevEmadiff;
			emaDiff_10_20_list.add(EMAYesFast - EMAYestSlow);
			
		}

		
		// For 5M interval
		// Get Fast EMA, try with different parameters Ex: 8,16,7 as we are
		// dealing with 5M candles
		fema = (double) Math.round(MovingAverageCalcs.CalculateEMA(todaysPrice,
				8, EMAYesterdayFast) * 100000) / 100000;
		// Get Slow EMA
		sema = (double) Math.round(MovingAverageCalcs.CalculateEMA(todaysPrice,
				20, EMAYesterdaySlow) * 100000) / 100000;
		
		// Get Slowest EMA
		sema50 = (double) Math.round(MovingAverageCalcs.CalculateEMA(todaysPrice,
						50, EMAYesterdaySlowest) * 100000) / 100000;
		double emaDiff = (double) Math.round((fema - sema) * 100000) / 100000;
		
		//Calculate the higher timeframe 4H in this case
		if (calc4H)
		{
			System.out.println("Calculating the 4H EMAs...wait..!!");
			if (EMA4HFAST !=0.0 || EMA4HSLOW == 0.0)
			{
			EMA4HFAST = EMAYesFast;
			EMA4HSLOW = EMAYestSlow;
			}
			fema4H = (double) Math.round(MovingAverageCalcs.CalculateEMA(todaysPrice,
					8, EMA4HFAST) * 100000) / 100000;
			// Get Slow EMA
			sema4H = (double) Math.round(MovingAverageCalcs.CalculateEMA(todaysPrice,
					20, EMA4HSLOW) * 100000) / 100000;
			
			double ema4HDiff = (double) Math.round((fema4H - sema4H) * 100000) / 100000;
			ema4HDiff_list.add(ema4HDiff);
			
		}
		
		//String diffStr = df.format(macdDiff);
		// Get signal EMA
		
		
		emaDiff_10_20_list.add(emaDiff);

		System.out.println("EMAs in EMACrossover(1H, 4H, ClosePrice,OpenPrice)->"+ fema +  "::" + sema + "::" + sema50 + "::" 
		+ fema4H +  "::" + sema4H +  "::" + todaysPrice + "::" + openPrice);
			
			// EMA crossover strategy, when slow EMA cross fast EMA & next higher timeframe EMA diff in same direction 
		
		
				
			if (emaDiff_10_20_list.size() > 1 && EMAYesterdayFast != 0.0 && EMAYesterdaySlow != 0.0 && EMAYesterdaySlowest !=0.0 && 
					EMA4HFAST != 0.0 && EMA4HSLOW != 0.0) {
				int index10_20 = emaDiff_10_20_list.size();
				if (((emaDiff_10_20_list.get(index10_20 - 2) <= 0.0 && emaDiff_10_20_list.get(index10_20 - 1) > 0.0 ))
						//&& sema > sema50 && todaysPrice > fema)
						||
						((emaDiff_10_20_list.get(index10_20 - 2) >= 0.0 && emaDiff_10_20_list.get(index10_20 - 1) < 0.0 ))
								
								//&& sema < sema50 && todaysPrice < fema)
						) {
					
					//Check if its a Bullish candle & (Fast EMA > Slow EMA && (Slow EMA > Slowest EMA OR CandleClose > SlowestEMA ) OR
					//Check if its a Bearish candle & (Fast EMA < Slow EMA && (Slow EMA < Slowest EMA OR CandleClose < SlowestEMA) 
					//AND EMA crossover is in same direction as 4H Or higher timeframe
					//NOT APPLIED NOW:: If the Slow(20) EMA doesn't cross the slowest (50) EMA, then check if the diff between CandleClose & FastEMA is more 
					//than the gap between Slow & Slowest EMA
					if((todaysPrice > openPrice && todaysPrice > fema && (sema > sema50 ||  todaysPrice > sema50)
							&& ema4HDiff_list.get(ema4HDiff_list.size() -1) > 0.0
							//|| Math.abs((todaysPrice - fema)) > Math.abs(sema - sema50) 
					)
							
							|| (todaysPrice < openPrice && todaysPrice < fema && (sema < sema50 || todaysPrice < sema50)
									&& ema4HDiff_list.get(ema4HDiff_list.size() -1) < 0.0
									//|| Math.abs((todaysPrice - fema)) > Math.abs(sema - sema50)  )
									))
					{

					System.out.println(symbol
							+ " EMA CROSSOVER CRITERIA FULFILLED ..EMAs, Close & Open Price of last 1H candle--> " );
							//+ fema + "::" + sema + "::" + sema50 + "::" + todaysPrice + "::" + openPrice);
					
					//Macd result consists of Macd,StopLoss & Extent of setting TP
					//If clean hit i.e all 3 EMAs are in sequence then R could be 2.0 else keep a conservative R of 1.2 Or 1.5
					emaResult[0] = emaDiff_10_20_list.get((index10_20 -1));
					emaResult[1] = (emaDiff_10_20_list.get((index10_20 -1)) > 0.0?Math.max(EMAYesterdaySlow,EMAYesterdayFast):Math.min(EMAYesterdaySlow,EMAYesterdayFast));
					emaResult[2] = ((todaysPrice > fema && sema > sema50) || (todaysPrice < fema && sema < sema50))?2.0:3.0;
					
					}
					else
						System.out.println("EMA CROSSOVER DETECTED BUT SIGNAL NOT GENERATED !! Closing price & Time -->" + todaysPrice + "::" + System.currentTimeMillis());
					
				}
			}	
			//}
			return emaResult;
		}  
		
		//TODO:
		/**
		 	1) Implement trading hours, NZDUSD, AUDJPY,USDJPY - no trading after 10:00 BST
			2) Check candle pattern (Green/Red) for triggering crossover ones
			3) Check MACD/EMA crossover in 30 Min chart
			
		**/
		
		
		
		// STRATEGY 2: Check Simpler strategy with 90% check only 
		//MODIFIED: To make it stronger, added 2 previous Macd checks 
			/*if (index > 2 ){
			if (EMAYest15MFast != 0.0 && EMAYest15MSlow != 0.0) {
			if ((((macdDiff > 0.0 && signal > 0.0) || (macdDiff < 0.0 && signal < 0.0)) && macd > 0.0 
					&& (macdMap.get(symbol).get(index - 3) >= 0.0 && macdMap.get(symbol).get(index - 2) > 0.0)
					&& Math.abs((0.9 * macdDiff)) > Math.abs(signal) && todaysPrice > fema && EMAYest15MFast > EMAYest15MSlow)
					|| (((macdDiff > 0.0 && signal > 0.0) || (macdDiff < 0.0 && signal < 0.0)) && macd < 0.0
							&& (macdMap.get(symbol).get(index - 3) <= 0.0 && macdMap.get(symbol).get(index - 2) < 0.0)
							&& Math.abs((0.9 * macdDiff)) > Math.abs(signal)
							&& todaysPrice < fema && EMAYest15MFast < EMAYest15MSlow)) {

				System.out.println(symbol
						+ " MACD CRITERIA FULFILLED..by  SIMPLE MACD 90% STRATEGY 2!!");
				emaResult[0] = macd;
				emaResult[1] = 2.0;
				return emaResult;
			}

		}
			}*/
			

}
