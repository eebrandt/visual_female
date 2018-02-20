
setwd("/home/eebrandt/projects/dissertation/chapter_1/female_choice/data/")
clypops <- read.csv("patrick_cly_trials.csv", header = T)

#subsets out only trials with both individuals from SR population
#note: we also only want trials that were accepted or rejected. "Aborts" do not count.
SR <- subset(clypops, clypops$male_pop == "SR" & clypops$female_pop == "SR" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
# important: this removes all empty "outcomes" from the data frame
SR <- droplevels(SR)

# turns the data into a nice summary table for plotting
SRcounts <- table(SR$outcome)
# converts the table to percentages
SRcounts <- (SRcounts/28) * 100

# same as above, only with hua/hua trials
hua <- subset(clypops, clypops$male_pop == "hua" & clypops$female_pop == "hua" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
hua <- droplevels(hua)
huacounts <- table(hua$outcome)
huacounts <- (huacounts/13) * 100

# same as above, only for trials with males from hua and females from SR
mhua_fSR <- subset(clypops, clypops$male_pop == "hua" & clypops$female_pop == "SR" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
mhua_fSR <- droplevels(mhua_fSR)
mhua_fSRcounts <- table(mhua_fSR$outcome)
mhua_fSRcounts <- (mhua_fSRcounts/22) * 100

# same as above, only for trials with males from SR and females from hua
mSR_fhua <- subset(clypops, clypops$male_pop == "SR" & clypops$female_pop == "hua" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
mSR_fhua <- droplevels(mSR_fhua)
mSR_fhuacounts <- table(mSR_fhua$outcome)
mSR_fhuacounts <- (mSR_fhuacounts/10) * 100

# diet treatment stuff

#subsets out by diet treatment rather than population
high <- subset(clypops, clypops$male_trt == "high" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
high <- droplevels(high)
highcounts <- table(high$outcome)
highcounts <- (highcounts/34) * 100

# same as for high diet
low <- subset(clypops, clypops$male_trt == "low" & (clypops$outcome == "accept" | clypops$outcome == "reject"))
low <- droplevels(low)
lowcounts <- table(low$outcome)
lowcounts <- (lowcounts/40) * 100

highSR <- subset(SR, SR$male_trt == "high" & (SR$outcome == "accept" | SR$outcome == "reject"))
highSR <- droplevels(highSR)
highSRcounts <- table(highSR$outcome)
highSRcounts <- (highSRcounts/12) * 100

lowSR <- subset(SR, SR$male_trt == "low" & (SR$outcome == "accept" | SR$outcome == "reject"))
lowSR <- droplevels(lowSR)
lowSRcounts <- table(lowSR$outcome)
lowSRcounts <- (lowSRcounts/16) * 100



### Plots
par(mfrow=c(2,2))
barplot(SRcounts, axes = F, ylim = c(0,100), col = c("white", "black"), main = "Male SR/Female SR")
axis(2, at = c( 0, 50, 100))
text(.75, 26, "21%")
text(1.9, 84, "79%")
box()

barplot(huacounts, ylim = c(0, 100), axes = F, col = c("white", "black"), main = "Male Hua/Female Hua")
axis(2, at = c(0, 50, 100))
text(.75, 20, "15%")
text(1.9, 90, "85%")
box()

barplot(mhua_fSRcounts, ylim = c(0, 100), axes = F, col = c("white", "black"), main = "Male Hua/Female SR")
axis(2, at = c(0, 50, 100))
text(.75, 37, "32%")
text(1.9, 73, "68%")
box()

barplot(mSR_fhuacounts, ylim = c(0, 100), col = c("white", "black"), axes = F, main = "Male SR/Female Hua")
axis(2, at = c(0, 50, 100))
text(.75, 15, "10%")
text(1.9, 95, "95%")
box()

## diet treatment plots
par(mfrow=c(2,2))
barplot(highcounts, axes = F, col = c("white", "black"), ylim = c(0, 100), main = "overall high diet")
axis(2, at = c(0, 50, 100))
text(.75, 26, "21%")
text(1.9, 84, "79%")
box()

barplot(lowcounts, axes = F, col = c("white", "black"), ylim = c(0, 100), main = "overall low diet")
axis(2, at = c(0, 50, 100))
text(.75, 28, "23%")
text(1.9, 84, "78%")
box()

# SR specifically
barplot(highSRcounts, axes = F, col = c("white", "black"), ylim = c(0, 100), main = "SR high diet")
axis(2, at = c(0, 50, 100))
text(.75, 38, "33%")
text(1.9, 72, "67%")
box()

barplot(lowSRcounts, axes = F, col = c("white", "black"), ylim = c(0, 100), main = "SR low diet")
axis(2, at = c(0, 50, 100))
text(.75, 18, "13%")
text(1.9, 93, "88%")
box()


