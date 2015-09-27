import re, codecs, unidecode

class GenderName:

    def __init__(self):
        self.es_male_names = [line.split(',')[0] for line in codecs.open('/Users/melisabok/tesis/gender-detection-py/resources/lists/spanish_male.csv', 'r', 'utf-8').readlines()]
        self.es_female_names = [line.split(',')[0] for line in codecs.open('/Users/melisabok/tesis/gender-detection-py/resources/lists/spanish_female.csv', 'r', 'utf-8').readlines()]

        self.es_male_names = [unidecode.unidecode(x) for x in self.es_male_names]
        self.es_female_names = [unidecode.unidecode(x) for x in self.es_female_names]

        self.es_male_names = filter(lambda x: x, self.es_male_names)
        self.es_female_names = filter(lambda x: x, self.es_female_names)

    def findMaleName(self, screen_name):
        for name in self.es_male_names:
            if screen_name.upper().startswith(name):
                return name
        return ''
        
    def findFemaleName(self, screen_name):
        for name in self.es_female_names:
            if screen_name.upper().startswith(name):
                return name
        return ''

    def get_gender_screen_name(self, screen_name):
        isMale = False
        isFemale = False
        male = self.findMaleName(screen_name)
        if male and len(male) >= 5:
            isMale = True
            #print screen_name + ': Male ' + male
        female = self.findFemaleName(screen_name)
        if female and len(female) >= 5:
            isFemale = True
            #print screen_name + ': Female ' + female
    
        if(isMale and isFemale):
            if (len(female) > len(male)):
                return u'Female'
            else:
                return u'UNKNOWN'
        elif(isMale):
            return 'Male'
        elif(isFemale):
            return 'Female'
        return u'UNKNOWN'

    def get_gender_name(self):
        return u'UNKNOWN'

if __name__ == '__main__':
    var = raw_input("Please enter something: ")
    print "Get gender for: " + var
    print GenderName().get_gender_screen_name(var)


