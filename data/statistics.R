# distribution of number of lemmas across synsets
# ===============================================

df.synsets <- read.table('input/synset_imagenet.txt', sep="\t", header=F, colClasses = c('factor', "character"))
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

# distribution of expansions per pattern

# returns (# processed expansions, # filtered expansions) for pattern i
nexpansions <- function(i) {
  output_file <- sprintf('output/processed_data/pattern_%d.txt', i)
  df.expansions <- read.table(output_file, sep="\t", header=F, colClasses = c('factor', "character", "character"))
  names(df.expansions) <- c('synset.id', 'lemma', 'expansionlist')
  df.expansions$expansions <- strsplit(trimws(df.expansions[,3]), ', ')
  df.expansions$nexpansions <- sapply(df.expansions$expansions, length)
  processed.expansions <- sum(df.expansions$nexpansions)
  
  output_file <- sprintf('output/filtered_data/pattern_%d.txt', i)
  df.expansions <- read.table(output_file, sep="\t", header=F, colClasses = c('factor', "character", "character"))
  names(df.expansions) <- c('synset.id', 'lemma', 'expansionlist')
  df.expansions$expansions <- strsplit(trimws(df.expansions[,3]), ', ')
  df.expansions$nexpansions <- sapply(df.expansions$expansions, length)
  filtered.expansions <- sum(df.expansions$nexpansions)
  return (c(processed.expansions, filtered.expansions))
}

nexpansions.vector <- sapply(1:7, nexpansions)
names(nexpansions.vector) <- c('*_ADJ [lemma]',
                              '[lemma] in the *',
                              '[lemma] is *_VERB',
                              '[lemma] was *_VERB',
                              '*_NOUN [lemma]',
                              '* [lemma]',
                              '[lemma] *')

# table and plot
pdf('expansion_distribution.pdf')
barplot(nexpansions.vector, las=3, ylab="number of expansions", beside = T)
dev.off()

