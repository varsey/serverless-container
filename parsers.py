import re
import string
from yargy import Parser, rule, or_
from yargy.predicates import dictionary, gram, type as t1

from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)


class Parsers():
    @staticmethod
    def parse_inn(card):
        INT = t1('INT')
        rule_inn1 = rule(
            dictionary({'инн'}),
            gram('NOUN').optional(),
            INT.repeatable().optional(),
            INT.repeatable()
        )
        parser_inn1 = Parser(rule_inn1)

        inn = ''
        for match in parser_inn1.findall(card):
            if len([x.value for x in match.tokens]) == 4:
                inn = ' '.join([x.value for x in match.tokens[1:]]).split(' ')[-2]
            else:
                inn = ' '.join([x.value for x in match.tokens[1:]]).replace(' ', '')

        return ''.join(re.findall(r'\d+', inn))

    @staticmethod
    def parse_corr_account(card):
        INT = t1('INT')
        rule_corr_account1 = rule(
            or_(
                dictionary({'к'}), dictionary({'кор'}), dictionary({'корр'}), dictionary({'корреспондентский'}),
                ),
            or_(
                dictionary({'сч'}), dictionary({'с'}), dictionary({'счет'}),
            ),
            gram('NOUN').optional(),
            INT.repeatable()
        )
        parser_corr_account1 = Parser(rule_corr_account1)

        rule_corr_account2 = rule(
            or_(
                dictionary({'корсчет'}), dictionary({'коррсчет'}), dictionary({'ксчет'}),
            ),
            gram('NOUN').optional(),
            INT.repeatable()
        )
        parser_corr_account2 = Parser(rule_corr_account2)

        corr_account = ''
        for match in parser_corr_account1.findall(card):
            corr_account = ' '.join([x.value for x in match.tokens[2:]]).replace(' ', '')

        if len(corr_account) == 0:
            for match in parser_corr_account2.findall(card):
                corr_account = ' '.join([x.value for x in match.tokens[2:]]).replace(' ', '')

        return ''.join(re.findall(r'\d+', corr_account))

    @staticmethod
    def parse_r_account(card):
        INT = t1('INT')
        rule_oper_account1 = rule(
            or_(
                dictionary({'р'}), dictionary({'расчсчет'}), dictionary({'расчетный'}), dictionary({'рас'}),
                ),
            or_(
                dictionary({'сч'}), dictionary({'с'}), dictionary({'счет'}),
            ),
            gram('NOUN').optional(),
            INT.repeatable()
        )
        parser_oper_account1 = Parser(rule_oper_account1)

        rule_oper_account2 = rule(
            or_(
                dictionary({'рсчет'}), dictionary({'расчсчет'}), dictionary({'рассчет'}),
            ),
            gram('NOUN').optional(),
            INT.repeatable()
        )
        parser_oper_account2 = Parser(rule_oper_account2)

        oper_account = ''
        for match in parser_oper_account1.findall(card):
            oper_account = ' '.join([x.value for x in match.tokens[2:]]).replace(' ', '')

        if len(oper_account) == 0:
            for match in parser_oper_account2.findall(card):
                oper_account = ' '.join([x.value for x in match.tokens[2:]]).replace(' ', '')

        return ''.join(re.findall(r'\d+', oper_account))

    @staticmethod
    def parse_bik(card):
        INT = t1('INT')
        rule_bik1 = rule(
            dictionary({'бик'}),
            gram('NOUN').optional(),
            INT.repeatable()
        )
        parser_bik1 = Parser(rule_bik1)

        bik = ''
        for match in parser_bik1.findall(card):
            bik = ' '.join([x.value for x in match.tokens[1:]]).split(' ')[-1]

        return bik

    @staticmethod
    def parse_kpp(card):
        INT = t1('INT')
        rule_kpp = rule(
            gram('NOUN').optional(),
            dictionary({'кпп'}),
            INT.repeatable().optional(),
            INT.repeatable()
        )
        parser_kpp1 = Parser(rule_kpp)

        kpp = ''
        for match in parser_kpp1.findall(card):
            kpp = ' '.join([x.value for x in match.tokens[1:]]).split(' ')[-1]

        return kpp

    @staticmethod
    def parse_tel(card):
        if len(card.lower().split('моб тел ')) >= 2:
                tel_part = card.lower().split('моб тел')
                return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        elif len(card.lower().split('тел ')) >= 2:
                tel_part = card.lower().split('тел')
                return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        elif len(card.lower().split('т ф ')) >= 2:
                tel_part = card.lower().split('т ф')
                return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        elif len(card.lower().split('телефон ')) >= 2:
            tel_part = card.lower().split('телефон')
            return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        elif len(card.lower().split('tel ')) >= 2:
            tel_part = card.lower().split('tel')
            return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        elif len(card.lower().split('phone ')) >= 2:
            tel_part = card.lower().split('phone')
            return ''.join(re.findall(r'\d+', tel_part[-1][:30]))[:11]
        else:
            return ''

    @staticmethod
    def get_website(message_text: str):
        exclude = list(filter(lambda x: x != '.' and x != '//' and x != ':', list(string.punctuation)))
        clean_text = message_text.replace("\n", " ")
        for ch in exclude:
            processed_txt = clean_text.replace(ch, ' ')
            clean_text = processed_txt
        while clean_text.count(2 * " ") > 0:
            clean_text = clean_text.replace(2 * " ", " ")

        if 'http' in clean_text:
            search = re.findall(r'(https?://\S+)', message_text)
            return min(search, key=len)
        elif 'www.' in clean_text:
            site = clean_text.split('www.')[-1].split(' ')[0]
            if site != '' and 'yandex' not in site and 'gmail' not in site and 'mail.ru' not in site and 'bk.ru' not in site:
                return 'www.' + site
        else:
            return ''

    @staticmethod
    def get_address(card: str):
        address = ''
        check = (
                    len(card.lower().replace('факту', '').split('факт')) > 1
                    and
                    len(card.lower().split('факт')[-1].split('дрес'))
        )
        if check > 1:
            address_in_message = ' '.join(card.split('акт')[1].split('дрес')[-1][:100].split(' ')[:10])
            try:
                address = ' '.join(
                    [' '.join((p.type, p.value)) for p in addr_extractor.find(address_in_message).fact.parts]
                )
            except Exception:
                address = ''
        address_clean = []
        for x in address.split(' '):
            if x not in address_clean:
                address_clean.append(x)
        return ' '.join(address_clean)

    @staticmethod
    def get_name(message_text: str, header_from: str):
        # TO-DO брать имя из подписи к имейлу в пересланном письме
        print(message_text)
        name_in_message_lst = []
        first, last, middle = '', '', ''
        if 'важением' in message_text:
            name_in_message_lst = (
                [
                    x for x in Parsers.clean_text(header_from + message_text.split('важением')[1]).split(' ')
                    if len(x) > 3 and x[0].isupper() and x[1].islower()
                ]
            )
        for n in range(len(name_in_message_lst)):
            name_in_message = ' '.join(name_in_message_lst[:n+1])
            try:
                first = names_extractor.find(name_in_message).fact.first
                last = names_extractor.find(name_in_message).fact.last
                middle = names_extractor.find(name_in_message).fact.middle
                first = '' if str(first) == 'None' else first
                last = '' if str(last) == 'None' else last
                middle = '' if str(middle) == 'None' else middle
                if n >= 1 and str(first) != '' and str(last) != '':
                    return first, last, middle

            except Exception as ex:
                print('cant parse names - ', ex)

        return first, last, middle

    @staticmethod
    def get_email(message_text, header_from):
        # TO-DO выводить имейлы с точкой
        punct = string.punctuation
        exclude = list(filter(lambda x: x != '@' and x != '.' and x != '<' and x != '>' and x != ':', list(punct)))
        clean_text = message_text.replace("\n", " ")
        for ch in exclude:
            processed_txt = clean_text.replace(ch, ' ')
            clean_text = processed_txt
        while clean_text.count(2 * " ") > 0:
            clean_text = clean_text.replace(2 * " ", " ")

        try:
            email = clean_text.split('From:')[1].split('To:')[0].split('<')[1].split('>')[0]
        except Exception:
            if "@" in header_from + clean_text:
                clean_text = header_from + ' ' + clean_text
                name_part = clean_text.split('@')[0]
                domain_part = clean_text.split('@')[1]
                email = name_part.split(' ')[-1].strip('<') + '@' + domain_part.split(' ')[0].strip('>')
                return email[7:] if 'mailto:' in email else email
            else:
                return ''

        return email[7:] if 'mailto:' in email else email

    @staticmethod
    def clean_text(text):
        exclude = set(string.punctuation + '№')
        clean_text = text.replace("\n", " ")
        for ch in exclude:
            processed_txt = clean_text.replace(ch, ' ')
            clean_text = processed_txt
        while clean_text.count(2 * " ") > 0:
            clean_text = clean_text.replace(2 * " ", " ")

        no_conseq_dupl = []
        cuts = clean_text.split(' ')
        for n, x in enumerate(cuts[:-1]):
            if cuts[n] != cuts[n+1]:
                no_conseq_dupl.append(x)
        no_conseq_dupl.append(cuts[-1])

        return " ".join(no_conseq_dupl)
