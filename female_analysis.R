setwd("~/projects/dissertation/chapter_1/female_choice/data")
# load data file
mating_data <- read.csv("trial_info.csv", sep = ",", header = TRUE, stringsAsFactors=FALSE)
setwd("~/projects/temp_trials/female_choice/analysis")

# divide up data between rounds 1 and 2, removing any rows for "redo" trials
mating_data <- subset(mating_data, outcome != "redo")

warm <- subset(mating_data, treatment == "warm")
room <- subset(mating_data, treatment == "room")
cold <- subset(mating_data, treatment == "cold")


wmrate <- sum(warm$outcome == "accept")/nrow(warm) *100
cdrate <- sum(cold$outcome == "accept")/nrow(cold)*100
rmrate<- sum(room$outcome == "accept")/nrow(room)*100

rates <- data.frame(cdrate,rmrate,wmrate)

row.names(rates) <- "acceptance rate"
colnames(rates)<- c("cold", "room", "warm")

ratesvec <- c(cdrate,rmrate,wmrate)
plot(ratesvec, type = "o", ylim = c(0, 75), axes = FALSE, ylab = "mating rate (%)", xlab = "temperature treatment", pch = 16)
axis(1, at=c(1,2,3), labels=c("cold", "room", "warm"))
axis(2, at=c(0, 25, 50, 75))
box()

ggplot(data=rates)  +
  geom_line()+
  geom_point()

#aes(x="treatment", y="mating rate", group=1))
