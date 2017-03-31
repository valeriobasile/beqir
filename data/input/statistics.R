# distribution of number of lemmas across synsets
# ===============================================

df.synsets <- read.table('synset_imagenet.txt', sep="\t", header=F, colClasses = c('factor', "character"))
names(df.synsets) <- c('synset.id', 'lemmalist')
df.synsets$lemmas <- strsplit(trimws(df.synsets[,2]), ', ')
df.synsets$nlemmas <- sapply(df.synsets$lemmas, length)

# table and plot
table(df.synsets$nlemmas)
pdf('lemma_distribution.pdf')
barplot(table(df.synsets$nlemmas), xlab = "number of lemmas", ylab="frequency (synsets)")
dev.off()

# distribution of number of words per lemma
# =========================================

df.lemmas <-data.frame(unlist(df.synsets$lemmas))
names(df.lemmas) <- c('lemma')
df.lemmas$lemma <- as.character(df.lemmas$lemma)
df.lemmas$words <- strsplit(trimws(df.lemmas$lemma), ' ')
df.lemmas$nwords <- sapply(df.lemmas$words, length)

# table and plot
table(df.lemmas$nwords)
pdf('word_distribution.pdf')
barplot(table(df.lemmas$nwords), xlab = "number of words", ylab="frequency (lemmas)")
dev.off()
