import csv
import matplotlib.pyplot as plt
import numpy as np
import random
import scipy.signal
import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
import math

###############################################################################   
def get_gradient(point1, point2):
    if point1[0] == point2[0]:
        print("WARNING", point1, point2)
    return (point2[1]-point1[1])/(point2[0]-point1[0])

def is_peak(close, days, day):
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1] <= value >= close[day+1]:
        return True
    return False

def is_trough(close, days, day):
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1] >= value <= close[day+1]:
        return True
    return False

def get_current(step, grad, left):
    return left[1] + (step-left[0])*grad

def shift_peaks(peaks, left_peak, margin):
    # Find peaks within the margin to the right
    rightmost_left = left_peak
    for peak in peaks[peaks.index(left_peak):]:
        if peak[1] > (1-margin)*left_peak[1]:
            rightmost_left = peak
    return rightmost_left

def shift_troughs(troughs, left_trough, margin):
    # Find troughs within the margin to the right
    rightmost_left = left_trough
    for trough in troughs[troughs.index(left_trough):]:
        if trough[1] < (1+margin)*left_trough[1]:
            rightmost_left = trough
    return rightmost_left

def trendline1(d, start_index, end_index):
    sell = ( 0, 0, 0 )
    buy = ( 0, 0, 0 )
    dates = []
    close = []
    closerough = []
    prev_close = 0
    prev_date = 0
    for i in range(start_index, end_index):
        if d[i, 0][-2:] == '01':            
            if prev_close > 0:
                dates.append(prev_date)
                close.append(float(prev_close))
        prev_close = d[i, 1]
        
    close = close[-60:]
    #plt.plot(dates, close, color="grey")
    peaks, q = scipy.signal.find_peaks(close, distance = 1)
    troughs, q = scipy.signal.find_peaks([-x for x in close], distance = 1) 
    peaks = np.concatenate(([0], peaks, [len(close)-1]))
    troughs = np.concatenate(([0], troughs, [len(close)-1]))
    i = 2
    sell_cross = 0
    buy_cross = 0
    state = 0 # start in a sell state
    while i < len(close):
        #print(state)
        if state == 0:
            if buy != (0, 0, 0) and close[i] > buy[1] + (i - buy[0])*buy[2]: 
               buy_cross = i-1
               #print("buy cross at", dates[i])
               state = 1 # shift into a buy state
        elif state == 1:
            if sell != (0, 0, 0) and close[i] < sell[1] + (i - sell[0])*sell[2]: 
               sell_cross = i-1
               #print("sell cross at", dates[i])
               state = 0 # shift into a buy state
        i += 1 #move to next day
        # If we are in a sell state - calculate buy line
        if state == 0:
            relevant_peaks = [x for x in peaks if x<= i]
            heights = [close[x] for x in relevant_peaks]
            h1 = max(heights)
            c1 = close.index(h1)
            bp1 = (c1, h1)
            barrier = max(sell_cross, c1)
            relevant_peaks = [x for x in peaks if (x<=i and x>barrier)]
            heights = [close[x] for x in relevant_peaks]
            if relevant_peaks:
                h2 = max(heights)
                c2 = relevant_peaks[heights.index(h2)]
                bp2 = (c2, h2)
                grad = (h2-h1)/(c2 - c1)
            else:
                bp2 = (bp1[0] + 6, bp1[1])
                grad = 0
            buy = (bp2[0], bp2[1], grad)
            #plt.plot([bp1[0], bp2[0]], [bp1[1], bp2[1]], color="green")
            
            i += 1 #move to next day
        # If we are in a buy state - calculate sell line
        elif state == 1:
            relevant_troughs = [x for x in troughs if x<= i]
            heights = [close[x] for x in relevant_troughs]
            h1 = min(heights)
            c1 = close.index(h1)
            sp1 = (c1, h1)
            barrier = max(buy_cross, c1)
            #print(i, dates[barrier])
            #print(troughs)
            relevant_troughs = [x for x in troughs if (x<=i and x>barrier)]
            heights = [close[x] for x in relevant_troughs]
            #print("relevant troughs: ", relevant_troughs)
            if relevant_troughs:
                h2 = min(heights)
                c2 = relevant_troughs[heights.index(h2)]
                sp2 = (c2, h2)
                grad = (h2-h1)/(c2 - c1)
            else:
                sp2 = (sp1[0] + 6, sp1[1])
                grad = 0
            sell = (sp2[0], sp2[1], grad)
            #plt.plot([sp1[0], sp2[0]], [sp1[1], sp2[1]], color="red")        
    #plt.plot([sp1[0], sp2[0]], [sp1[1], sp2[1]], color="orange")  
    #plt.plot([bp1[0], bp2[0]], [bp1[1], bp2[1]], color="yellow")                
    #plt.show()
    return state
    
    
#name = "ABP.AX"
#with open(f"{name}.csv") as file:
#    data = pd.read_csv(file)
#    three_point_TL(data, 0, 3000)

def trendline2(d, step):
    
    print(d)
    left_peak = (None, 0)
    right_peak = (None, 0)
    left_trough = (None, 1000000) # assuming no stock is ever valued 1000000 a share
    right_trough = (None, 1000000)
    # Step through the 60 months, or however many are available
    close = [] # Comment out if not plotting
    steps = [] # Comment out if not plotting
    for i in range(min(step//30-1, 60)):
        
        
        # If this month is strictly greater than the left peak, then the left peak
        # becomes the right peak, and this new one becomes the left peak
        value = d[step-30*i, 1]
        if math.isnan(value):
            value = d[step-30*i+1, 1]
        if math.isnan(value):
            value = d[step-30*i-1, 1]
            
        if value > left_peak[1]:
            right_peak = left_peak
            left_peak = (step-30*i, value)
        
        close.append(value) # Comment out if not plotting
        steps.append(step-30*i) # Comment out if not plotting
        
        # If we have a value, and it is less than the previous lowest,
        # it becomes the new lowest, and the old lowest becomes the left point
        if value > 0 and value < left_trough[1]:
            right_trough = left_trough
            left_trough = (step-30*i, value)
            
    if right_peak[0] == None or left_peak[0] == None:
        return None, None
    buy_grad = (right_peak[1]-left_peak[1])/(right_peak[0]-left_peak[0])
    sell_grad = (right_trough[1]-left_trough[1])/(right_trough[0]-left_trough[0])
    
    buy = right_peak[1] + (step-right_peak[0])*buy_grad
    sell = right_trough[1] + (step-right_trough[0])*sell_grad
    
    close.reverse() # Comment out if not plotting
    steps.reverse() # Comment out if not plotting
    plt.plot(steps, close) # Comment out if not plotting
    plt.plot([left_peak[0], right_peak[0], step], [left_peak[1], right_peak[1], buy], color= "green")
    plt.plot([left_trough[0], right_trough[0], step], [left_trough[1], right_trough[1], sell], color= "red")# Comment out if not plotting
    plt.show() # Comment out if not plotting
    return buy, sell

MOE = 0.03

def trendline3(d, step):
    # HEAVY COMMENTING USED FOR EXPLANATION
    
    # ONLY WORKS IF WE START PLOTTING ON A DAY WITH A CLOSING PRICE
        
    start = max(0, step-365*5)
    # We originally get all of our monthly points, by accessing, the 
    # array indexed at "start", and we iterate until our 
    # current position: "step"
    
    while math.isnan(d[start, 1]) or math.isnan(d[start+1, 1]):
        start += 1
    # We keep stepping forward until we find two consecutive days with closing
    # prices    
    
    left_peak = (start, d[start,1]) 
    right_peak = (start+1, d[start+1,1])
    left_trough = (start, d[start,1])
    right_trough = (start+1, d[start+1,1])
    # We have now initialized our peaks and troughs in a specific way.
    # We set our first point as both our lowest trough, and highest peak.
    # We then set our second point as the second lowest and second highest.
    # This might not be strictly correct, but will be corrected for once we start 
    # iterating.
    
    #COMMENT OUT IF NOT PLOTTING -- IGNORE IF TONY --
    days = []
    prices = []
    
    pos = start+30
    while pos < step:
        
        while math.isnan(d[pos, 1]): 
            pos+=1
        # If we dont have a closing price that day, we keep stepping forward
        # until we find one (this will give us ~ 1 month gaps, but not exactly)
        value = d[pos, 1]         
        
        if value > left_peak[1] or abs(value-left_peak[1]) < left_peak[1]*MOE: # If this is a new highest point or within 0.5% of previous
        
            left_peak = (pos, value) # We make this our new left_peak
            right_peak = (pos+1, 0) # Make the next point our right_peak
            
        # I suspect that the below section may cause issue when reseting buy lines
        if value < left_trough[1] or abs(value-left_trough[1]) < left_trough[1]*MOE: # If this is a new lowest point
        
            left_trough = (pos, value) # We make this our new left_trough
            right_trough = (pos+1, 1000000) # Make the next point our right_trough
            
            # This is now a sell, so we must also reset our right peak.
            right_peak = (pos+1, 0) # Make the next point our right_peak 
        
        b_grad = (right_peak[1]-left_peak[1])/(right_peak[0]-
                                                   left_peak[0])
        s_grad = (right_trough[1]-left_trough[1])/(right_trough[0]-
                                                   left_trough[0])
        buy = left_peak[1] + b_grad*(pos-left_peak[0])
        sell = left_trough[1] + s_grad*(pos-left_trough[0])
        
        # Calculate the buy and sell price at this point.
        # Now we can see if we are above or below these lines.
        
        if value < sell: # We have crossed our sell line. Now we have to reset the right.

            right_trough = (pos, value)
            
            right_peak = (pos+1, 0) # Make the next point our right_peak
            
        elif value > buy: # We have crossed our buy line. No problem, just move the right peak
            
            right_peak = (pos, value)
        
        #COMMENT OUT IF NOT PLOTTING -- IGNORE IF TONY --
        days.append(pos)
        prices.append(value)
        
        pos += 30 # We are finished and move on to the next month
    
    b_grad = (right_peak[1]-left_peak[1])/(right_peak[0]-
                                                   left_peak[0])
    s_grad = (right_trough[1]-left_trough[1])/(right_trough[0]-
                                                   left_trough[0])
    buy = left_peak[1] + b_grad*(step-left_peak[0])
    sell = left_trough[1] + s_grad*(step-left_trough[0])
    #PLOTTING -- IGNORE IF TONY --
    print(left_peak[0], right_peak[0], step)
    print(left_peak[1], right_peak[1], buy)
    plt.plot(days, prices) # Comment out if not plotting
    plt.plot([left_peak[0], right_peak[0], step], [left_peak[1], right_peak[1], buy], color= "green") # Comment out if not plotting
    plt.plot([left_trough[0], right_trough[0], step], [left_trough[1], right_trough[1], sell], color= "red") # Comment out if not plotting
    plt.show() # Comment out if not plotting
    
    step_value = d[step, 1] # Todays closing price
    print(step_value)
    if step_value >= buy and step_value <= sell: # Schrodinger
        return -1 # sell 
    elif step_value < buy and step_value > sell: # Hold
        return 0 # do nothing
    elif step_value >= buy: # Above buy line
        return 1 # buy
    elif step_value <= sell: # Below sell line
        return -1 # sell
   

def trendline4(d, step, years, plot, use_peaks, margin):
    start_step = max(0, step-365*years)
    while math.isnan(d[start_step, 1]): # Step forward until we find a valid point
        start_step += 5 # jumps of 5 days because why not?
    # USE MONTH JUMPS TO SPEED UP COMPUTATION
    #today = dt.datetime.strptime(d[step, 0], "%Y-%m-%d")
    close = []
    days = []
    at = start_step
    while at < step:
        #date = dt.datetime.strptime(d[at, 0], "%Y-%m-%d")
        if d[at, 0][-2:] == "01": # We found the start of a new month
            month_end = at - 1
            for i in range(15): # if we cant get a value in 15 days give up
                value = d[month_end, 1]
                if not math.isnan(value):
                    close.append(value)
                    days.append(month_end)
                    #days.append(dt.datetime.strptime(d[month_end, 0], "%Y-%m-%d"))
                    break
                month_end -= 1
        at += 1
    if len(days) < 3:
        return 0
    ###############################################################################   
        
    left_peak = (0, 0)
    left_trough = (0, 1000000)
    
    if use_peaks == 0: # doesn't require peaks
        for day in range(0, len(days)):
            value = close[day]  
            # If it is higher than a margin of error below highest peak
            if value > left_peak[1]*(1-margin): 
                left_peak = (days[day], close[day])
                #if day == len(days) - 1:
                right_peak = (left_peak[0], 0)
                b_grad = 0
                #else:
                #    right_peak = (days[day+1], 0)
                #   b_grad = get_gradient(left_peak, right_peak)  
            if value < left_trough[1]*(1+margin): # If it is lower than a margin of error above the lowest trough
                left_trough = (days[day], close[day])
                #if day == len(days) - 1:
                right_trough = (left_trough[0], 1000000)
                s_grad = 0
                #else:
                #    right_trough = (days[day+1], 1000000)
                #    s_grad = get_gradient(left_trough, right_trough)
                
    elif use_peaks == 1: # requires peaks
        for day in range(0, len(days)):
            value = close[day]  
            if value > left_peak[1]*(1-margin) and is_peak(close, days, day): # If it is higher than a margin of error below highest peak
                left_peak = (days[day], close[day])
                #if day == len(days) - 1:
                right_peak = (left_peak[0], 0)
                b_grad = 0
                #else:
                #    right_peak = (days[day+1], 0)
                #   b_grad = get_gradient(left_peak, right_peak)               
            if value < left_trough[1]*(1+margin) and is_trough(close, days, day): # If it is lower than a margin of error above the lowest trough
                left_trough = (days[day], close[day])   
                #if day == len(days) - 1:
                right_trough = (left_trough[0], 1000000)
                s_grad = 0
                #else:
                #    right_trough = (days[day+1], 1000000)
                #    s_grad = get_gradient(left_trough, right_trough)
                    
    ###############################################################################
       
    if use_peaks == 0: # doesn't require peaks
        # Calculate the sell line
        for day in range(days.index(left_trough[0])+1, len(days)):
            sell = get_current(days[day], s_grad, left_trough)
            value = close[day]   
            if value < sell and days[day] < left_peak[0]: # we went under the sell line before the left peak, so get a new sell line.
                right_trough = (days[day], close[day])
                s_grad = get_gradient(left_trough, right_trough)     
            elif value < right_trough[1]*(1+MOE) :
                right_trough = (days[day], close[day])
                s_grad = get_gradient(left_trough, right_trough)                        
        # Calculate the buy line       
        for day in range(days.index(left_peak[0])+1, len(days)):
            buy = get_current(days[day], b_grad, left_peak)
            value = close[day]
            if value > buy and days[day]< left_trough[0]: # we went over the buy line before the left trough to get a new buy line
                right_peak = (days[day], close[day])
                b_grad = get_gradient(left_peak, right_peak)   
            elif value > right_peak[1]*(1-MOE):
                right_peak = (days[day], close[day])
                b_grad = get_gradient(left_peak, right_peak)  
                
    if use_peaks == 1: # requires peaks
        # Calculate the sell line
        for day in range(days.index(left_trough[0])+1, len(days)):
            sell = get_current(days[day], s_grad, left_trough)
            value = close[day]        
            if value < sell and days[day] < left_peak[0] and is_trough(close, days, day): # we went under the sell line before the left peak, so get a new sell line.
                right_trough = (days[day], close[day])
                s_grad = get_gradient(left_trough, right_trough)
            elif value < right_trough[1]*(1+MOE) and is_trough(close, days, day):
                right_trough = (days[day], close[day])
                s_grad = get_gradient(left_trough, right_trough)
        # Calculate the buy line       
        for day in range(days.index(left_peak[0])+1, len(days)):
            buy = get_current(days[day], b_grad, left_peak)
            value = close[day]   
            if value > buy and days[day] < left_trough[0] and is_peak(close, days, day): # we went over the buy line before the left trough to get a new buy line
                right_peak = (days[day], close[day])
                b_grad = get_gradient(left_peak, right_peak)  
            elif value > right_peak[1]*(1-MOE) and is_peak(close, days, day):
                right_peak = (days[day], close[day])
                b_grad = get_gradient(left_peak, right_peak)  
                
    ##############################################################################        
    buy = get_current(step, b_grad, left_peak)
    sell = get_current(step, s_grad, left_trough)
    if plot:
        print(left_peak, right_peak, (step, d[step, 1]))
        print(buy)
        print(left_trough, right_trough, (step, d[step, 1]))
        print(sell)
        plt.plot(days, close)
        plt.plot([left_peak[0], step], [left_peak[1], buy], color = "green")
        plt.plot([left_trough[0], step], [left_trough[1], sell], color = "red")
    if buy > d[step, 1] > sell: # below buy above sell, do nothing
        return 0
    elif buy <= d[step, 1] and sell <= d[step, 1]: # above buy and sell, buy
        return 1
    elif buy < d[step, 1] < sell: 
        return 0
    elif d[step, 1] < sell: 
        return -1


###############################################################################

def trendline5(d, step, years, plot, margin):
    start_step = max(0, step-365*years)
    while math.isnan(d[start_step, 1]): # Step forward until we find a valid point
        start_step += 5 # jumps of 5 days because why not?
        if start_step > step: # If we get back to where we started no bueno
            return 0
    # USE MONTH JUMPS TO SPEED UP COMPUTATION
    #today = dt.datetime.strptime(d[step, 0], "%Y-%m-%d")
    close = []
    days = []
    at = start_step
    while at < step:
        #date = dt.datetime.strptime(d[at, 0], "%Y-%m-%d")
        if d[at, 0][-2:] == "01": # We found the start of a new month
            month_end = at - 1
            for i in range(15): # if we cant get a value in 15 days give up
                value = d[month_end, 1]
                if not math.isnan(value):
                    close.append(value)
                    days.append(month_end)
                    #days.append(dt.datetime.strptime(d[month_end, 0], "%Y-%m-%d"))
                    break
                month_end -= 1
        at += 1
    if len(days) < 3:
        return 0
    ###############################################################################   
    # 1-> get a list of all the peaks in the graph, as well as their height
    # 2-> get a list of all the troughs in the graph as well as their height
    # 3-> Find the heighest preak in the graph
    # 4-> If there is no lower peak to the right, repeat 3 with the peaks
    # to the left of this peak
    # 5-> Find the lowest trough in the graph
    # 6-> IF there is no higher trough to the right, repeat 5 with the troughs
    # to the left of this trough
    # 7-> Start stepping through days from whichever of the lowest trough or
    # highest peak is left-most.
    # 8-> If a peak it higher than our right peak (default 0) and less than
    # our left peak, we pick it as our right points
    # 9-> Iterate through future peaks to see if any are under the line from
    # the left peak to the right peak. If they are, and before the start of the
    # sell line then make it the new right peak.
    # 10-> repeat steps 8-9 with troughs.
    
    # Get the peaks and troughs
    peaks = []
    troughs = []
    for i in range(len(days)):
        if is_peak(close, days, i):
            peaks.append((days[i], close[i]))
        elif is_trough(close, days, i):
            troughs.append((days[i], close[i]))
    # Find the appropriate max and min peaks following steps 3-4 and 5-6
    if len(peaks) < 2 or len(troughs) < 2:
        return 0
    left_peak = max(peaks, key = lambda x: x[1])
    left_peak = shift_peaks(peaks, left_peak, margin)
    left_trough = min(troughs, key = lambda x: x[1])
    left_trough = shift_troughs(troughs, left_trough, margin)
    while left_peak == peaks[-1]:
        peaks.pop(-1)
        # If we have less than 2 troughs give up.
        if len(peaks) < 2:
            return 0
        
        left_peak = max(peaks, key = lambda x: x[1])
        left_peak = shift_peaks(peaks, left_peak, margin)
    while left_trough == troughs[-1]:
        troughs.pop(-1)
        # If we have less than 2 troughs give up.
        if len(troughs) < 2:
            return 0
        left_trough = min(troughs, key = lambda x: x[1])
        left_trough = shift_troughs(troughs, left_trough, margin)
    # Set the right peak deafult as the peak immediately to the right of 
    # the left peak
    right_peak = peaks[peaks.index(left_peak)+1]
    # step the right peak through
    for peak in peaks[peaks.index(right_peak):]:
        # current peak is greater than right peak, swap
        if peak[1] > right_peak[1]:
            right_peak = peak
        # If current peak is over the buy line & before the left trough, swap
        b_grad = get_gradient(left_peak, right_peak)
        if (left_peak[1] + (peak[0]-left_peak[0])*b_grad < peak[1] and 
              peak[0] < left_trough[0]):
            right_peak = peak
    # Set the right trough deafult as the peak immediately to the right of 
    # the left trough
    right_trough = troughs[troughs.index(left_trough)+1]
    for trough in troughs[troughs.index(right_trough):]:
        # current peak is greater than right peak, swap
        if trough[1] < right_trough[1]:
            right_trough = trough
        # If current trough is under the sell line & before the left peak, swap
        s_grad = get_gradient(left_trough, right_trough)
        if (left_trough[1]+(trough[0]-left_trough[0])*s_grad > trough[1] and 
             trough[0] < left_peak[0]):
            right_trough = trough
    # Find right peak and trough within the margin to the right 
    ############### THIS PART MAKES NO SENSE AND IS BAD #######################
    for peak in peaks[peaks.index(right_peak):]:
        if peak[1] > (1-margin)*right_peak[1]:
            right_peak = peak   
    for trough in troughs[troughs.index(right_trough):]:
        if trough[1] < (1+margin)*right_trough[1]:
            right_trough = trough 
    b_grad = get_gradient(left_peak, right_peak)   
    s_grad = get_gradient(left_trough, right_trough)
    buy = get_current(step, b_grad, left_peak)
    sell = get_current(step, s_grad, left_trough)
    if plot:
        print(left_peak, right_peak, (step, d[step, 1]))
        print(buy)
        print(left_trough, right_trough, (step, d[step, 1]))
        print(sell)
        
        plt.plot(days, close)
        plt.plot([left_peak[0], right_peak[0], step], [left_peak[1], right_peak[1], buy], color = "green")
        plt.plot([left_trough[0], right_trough[0], step], [left_trough[1], right_trough[1], sell], color = "red")
    if buy > d[step, 1] > sell: # below buy above sell, do nothing
        if plot:
            plt.title("HOLD")
        return 0
    elif buy <= d[step, 1] and sell <= d[step, 1]: # above buy and sell, buy
        if plot:
            plt.title("BUY")
        return 1
    elif buy < d[step, 1] < sell: 
        if plot:
            plt.title("HOLD")
        return 0
    elif d[step, 1] < sell:
        if plot:
            plt.title("SELL")
        return -1
        
        
        
        
def is_peak2(close, days, day):
    # Using a 1% margin for what is a peak
    margin= 0.01
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1]*(1-margin) <= value >= close[day+1]*(1-margin):
        return True
    return False

def is_trough2(close, days, day):
    # Using a 1% margin for what is a trough
    margin = 0.01
    value = close[day]
    if day == 0 or day == len(days) - 1:
        return False
    elif close[day-1]*(1+margin) >= value <= close[day+1]*(1+margin):
        return True
    return False

def trendline6(d, step, years, plot, margin):
    start_step = max(0, step-365*years)
    while math.isnan(d[start_step, 1]): # Step forward until we find a valid point
        start_step += 5 # jumps of 5 days because why not?
        if start_step > step: # If we get back to where we started no bueno
            return 0
    # USE MONTH JUMPS TO SPEED UP COMPUTATION
    #today = dt.datetime.strptime(d[step, 0], "%Y-%m-%d")
    close = []
    days = []
    at = start_step
    while at < step:
        #date = dt.datetime.strptime(d[at, 0], "%Y-%m-%d")
        if d[at, 0][-2:] == "01": # We found the start of a new month
            month_end = at - 1
            for i in range(15): # if we cant get a value in 15 days give up
                value = d[month_end, 1]
                if not math.isnan(value):
                    close.append(value)
                    days.append(month_end)
                    #days.append(dt.datetime.strptime(d[month_end, 0], "%Y-%m-%d"))
                    break
                month_end -= 1
        at += 1
    if len(days) < 3:
        return 0
    ###############################################################################   
    # 1-> get a list of all the peaks in the graph, as well as their height
    # 2-> get a list of all the troughs in the graph as well as their height
    # 3-> Find the heighest preak in the graph
    # 4-> If there is no lower peak to the right, repeat 3 with the peaks
    # to the left of this peak
    # 5-> Find the lowest trough in the graph
    # 6-> IF there is no higher trough to the right, repeat 5 with the troughs
    # to the left of this trough
    # 7-> Start stepping through days from whichever of the lowest trough or
    # highest peak is left-most.
    # 8-> If a peak it higher than our right peak (default 0) and less than
    # our left peak, we pick it as our right points
    # 9-> Iterate through future peaks to see if any are under the line from
    # the left peak to the right peak. If they are, and before the start of the
    # sell line then make it the new right peak.
    # 10-> repeat steps 8-9 with troughs.
    
    # Get the peaks and troughs
    peaks = []
    troughs = []
    for i in range(len(days)):
        if is_peak2(close, days, i):
            peaks.append((days[i], close[i]))
        elif is_trough2(close, days, i):
            troughs.append((days[i], close[i]))
    if len(peaks) < 2 or len(troughs) < 2:
        return 0
    
    # Find the appropriate max and min
    left_peak = max(peaks, key = lambda x: x[1])
    left_peak = shift_peaks(peaks, left_peak, margin)
    left_trough = min(troughs, key = lambda x: x[1])
    left_trough = shift_troughs(troughs, left_trough, margin)
    
    # Buy if is 5 year peak
    if left_peak[1] == close[-1]:
        return 1
    
    # Find the appropriate max and min peaks following steps 3-4 and 5-6
    while left_peak == peaks[-1]:
        peaks.pop(-1)
        # If we have less than 2 troughs give up.
        if len(peaks) < 2:
            return 0
        left_peak = max(peaks, key = lambda x: x[1])
        left_peak = shift_peaks(peaks, left_peak, margin)
    while left_trough == troughs[-1]:
        troughs.pop(-1)
        # If we have less than 2 troughs give up.
        if len(troughs) < 2:
            return 0
        left_trough = min(troughs, key = lambda x: x[1])
        left_trough = shift_troughs(troughs, left_trough, margin)
        
    # Set the right peak default as the peak immediately to the right of 
    # the left peak
    right_peak = peaks[peaks.index(left_peak)+1]
    # step the right peak through
    for peak in peaks[peaks.index(right_peak):]:
        # current peak is greater than right peak, swap
        if peak[1] > right_peak[1]:
            right_peak = peak
        # If current peak is over the buy line & before the left trough, swap
        b_grad = get_gradient(left_peak, right_peak)
        if left_peak[1] + (peak[0]-left_peak[0])*b_grad < peak[1]:
            right_peak = peak
    # Set the right trough deafult as the peak immediately to the right of 
    # the left trough
    right_trough = troughs[troughs.index(left_trough)+1]
    for trough in troughs[troughs.index(right_trough):]:
        # current peak is greater than right peak, swap
        if trough[1] < right_trough[1]:
            right_trough = trough
        # If current trough is under the sell line & before the left peak, swap
        s_grad = get_gradient(left_trough, right_trough)
        if left_trough[1]+(trough[0]-left_trough[0])*s_grad > trough[1]:
            right_trough = trough
    # Find right peak and trough within the margin to the right 
    ############### THIS PART MAKES NO SENSE AND IS BAD #######################
    for peak in peaks[peaks.index(right_peak):]:
        if peak[1] > (1-margin)*right_peak[1]:
            right_peak = peak   
    for trough in troughs[troughs.index(right_trough):]:
        if trough[1] < (1+margin)*right_trough[1]:
            right_trough = trough 
    b_grad = get_gradient(left_peak, right_peak)   
    s_grad = get_gradient(left_trough, right_trough)
    buy = get_current(step, b_grad, left_peak)
    sell = get_current(step, s_grad, left_trough)
    if plot:
        print(left_peak, right_peak, (step, d[step, 1]))
        print(buy)
        print(left_trough, right_trough, (step, d[step, 1]))
        print(sell)
        
        plt.plot(days, close)
        plt.plot([left_peak[0], right_peak[0], step], [left_peak[1], right_peak[1], buy], color = "green")
        plt.plot([left_trough[0], right_trough[0], step], [left_trough[1], right_trough[1], sell], color = "red")
    if buy > d[step, 1] > sell: # below buy above sell, do nothing
        if plot:
            plt.title("HOLD")
        return 0
    elif buy <= d[step, 1] and sell <= d[step, 1]: # above buy and sell, buy
        if plot:
            plt.title("BUY")
        return 1
    elif buy < d[step, 1] < sell: 
        if plot:
            plt.title("HOLD")
        return 0
    elif d[step, 1] < sell:
        if plot:
            plt.title("SELL")
        return -1
    


##############################################################################
def too_close(points, current, space):
    for point in points:
        if abs(point[0] - current[0]) < space:
            return 1
    return 0
def find_peaks(peaks, margin, n):
    highest = []
    for j in range(5):
        i = 1
        peak = peaks[0]
        while i < len(peaks):
            if peaks[i][1] > (1-margin)*peak[1] and peaks[i] not in highest and peaks[i] != sorted(peaks[i:], key=lambda x: x[1])[0]:
                if len(highest) == 0 or not too_close(highest, peaks[i], 90):
                    peak = peaks[i]
            i += 1
        if peak not in highest:
            highest.append(peak)
    return highest
                
def find_troughs(troughs, margin, n):
    lowest = []
    for j in range(5):
        i = 0
        trough = troughs[0]
        while i < len(troughs):
            if troughs[i][1] < (1+margin)*trough[1] and troughs[i] not in lowest and troughs[i] != sorted(troughs[i:], key=lambda x: x[1], reverse=True)[0]:
                if len(lowest) == 0 or not too_close(lowest, troughs[i], 90): #if within 90 days, consider flat
                    trough = troughs[i]
            i += 1
        if trough not in lowest:
            lowest.append(trough)     
    return lowest
                
# This section is inefficient, but it will have to do for now.       
        
    
    
    
def trendline7(d, step, years, plot, margin):
    start_step = max(0, step-365*years)
    #while math.isnan(d[start_step, 1]): # Step forward until we find a valid point
    #    start_step += 5 # jumps of 5 days because why not?
    #   if start_step > step: # If we get back to where we started no bueno
    #        return 0
    # USE MONTH JUMPS TO SPEED UP COMPUTATION
    #today = dt.datetime.strptime(d[step, 0], "%Y-%m-%d")
    close = []
    days = []
    at = step
    new_month = False
    while at > start_step:
        if d[at, 0][-2:] == "01": # We found the start of a new month |NEED BETTER SOLUTION|
            new_month = True
        at -= 1
        if new_month:
            value = d[at, 1]
            if not math.isnan(value):
                close.append(value)
                days.append(at)
                new_month = False
    if len(days) < 3:
        return 0
    days.reverse()
    close.reverse()
    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.set_facecolor("grey")
        fig.patch.set_facecolor("grey")
        ax.plot(days, close, color = "black")
    
    peaks = []
    troughs = []
    for i in range(len(days)):
        if is_peak2(close, days, i):
            peaks.append([days[i], close[i]])
        elif is_trough2(close, days, i):
            troughs.append([days[i], close[i]])     
    if len(peaks) < 2 or len(troughs) < 2:
        return 0
    greatest_peaks = find_peaks(peaks, margin, 5)
    lowest_troughs = find_troughs(troughs, margin, 5)
    if plot:
        p_close = [peak[1] for peak in greatest_peaks]
        p_days = [peak[0] for peak in greatest_peaks]
        t_close = [trough[1] for trough in lowest_troughs]
        t_days = [trough[0] for trough in lowest_troughs]
        ax.scatter(p_days, p_close, color = "lime")
        ax.scatter(t_days, t_close, color = "deeppink")
    # Find the sell line:
    sell_lines = []
    for i in range(len(lowest_troughs)):
        T1 = lowest_troughs[i]
        index = troughs.index(T1)
        lowest = 1000000
        T2 = (0, 1000000) #arbitrarily high value
        T3 = troughs[-1]
        grad = 1000000 #arbitrarily high value
        for trough in troughs[index+1:]:
            if trough[1] < (trough[0]-T1[0])*grad + T1[1]: # if our line is crossed
                if trough[1] > T1[1]:
                    T2 = trough
                    grad = get_gradient(T1, T2)
                elif trough[1] <= T1[1]:
                    T3 = trough   
        if T2[0]: # We add this line, only if we found a T2
            sell_lines.append((T1, get_gradient(T1, T2), T3))
    #if plot:
        #for line in sell_lines:
            #sell = line[0][1] + (step-line[0][0])*line[1]
            #ax.plot([line[0][0], step], [line[0][1], sell], color = "thistle")
    
    for trough in troughs:
        crossed = [line for line in sell_lines if get_current(trough[0], line[1], line[0]) > trough[1]]
        if len(crossed) == len(sell_lines):
            sell_lines.sort(key = lambda x: x[0][0])
            break
        sell_lines = [line for line in sell_lines if line not in crossed]
    sell_line = sell_lines[0]
    sell = sell_line[0][1] + (step-sell_line[0][0])*sell_line[1]
    if plot:     
        ax.plot([sell_line[0][0], step], [sell_line[0][1], sell], color = "deeppink")
    
    
    # Find the buy line
    buy_lines = []
    for i in range(len(greatest_peaks)):
        P1 = greatest_peaks[i]
        if P1 == peaks[-1]:
            continue
        index = peaks.index(P1)
        P2 = (0, 0) #arbitrarily low value
        grad = -10000000 #arbitrarily low value
        P3 = peaks[-1]
        for peak in peaks[index+1:]:
            if peak[1] > (peak[0]-P1[0])*grad + P1[1]: # if our line is crossed
                if peak[1] < P1[1]:
                    P2 = peak
                    grad = get_gradient(P1, P2)
                elif peak[1] >= P1[1]:
                    P3 = peak   
        if P2[0]: # We add this line, only if we found a T2
            buy_lines.append((P1, get_gradient(P1, P2), P3))
    #if plot:    
        #for line in buy_lines:
            #buy = line[0][1] + (step-line[0][0])*line[1]
            #ax.plot([line[0][0], step], [line[0][1], buy], color = "paleturquoise")
    buy_lines.sort(key = lambda x: x[0][0])
    
    for peak in peaks:
        crossed = [line for line in buy_lines if get_current(peak[0], line[1], line[0]) < peak[1]]
        if len(crossed) == len(buy_lines):
            buy_lines.sort(key = lambda x: x[0][0])
            break
        buy_lines = [line for line in buy_lines if line not in crossed]
    buy_line = buy_lines[0]
    buy = buy_line[0][1] + (step-buy_line[0][0])*buy_line[1]
    
    
    if plot:
        ax.plot([buy_line[0][0], step], [buy_line[0][1], buy], color = "lime")
        
    if buy > d[step, 1] > sell: # below buy above sell, do nothing
        if plot:
            plt.title("HOLD")
        return 0
    elif buy <= d[step, 1] and sell <= d[step, 1]: # above buy and sell, buy
        if plot:
            plt.title("BUY")
        return 1
    elif buy < d[step, 1] < sell: 
        if plot:
            plt.title("HOLD")
        return 0
    elif d[step, 1] < sell:
        if plot:
            plt.title("SELL")
        return -1        
            