import os
import re

import pandas
import pdfkit
from time import sleep

import repository
from dotenv import load_dotenv
import telegram.constants
from datetime import date, datetime

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

(
    CONFIRM,
    FIRST_NAME,
    LAST_NAME,
    BIRTH_DATE,
    GENDER,
    VACANCY_TYPE,
    SPECIALTY,
    SPECIFIC,
    MATH,
    PORT,
    HIST_GEO,
    ENG,
    END,
    EDIT,
    CANCEL
) = range(15)

# Regex:
r_name = r'^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.\'-]+$'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text('Hop, candidato(a)! Eu sou o <b>MiliBot</b>, o bot que te auxilia a calcular a sua '
                                    '<b>média</b> e te inserir no <b>ranking</b> de candidatos à <b>ESA 2022/2023</b> '
                                    '- se você quiser, claro - que será divulgado diariamente no grupo informado ao '
                                    'final.\n\n'
                                    'Recomendo que você veja mais <b>informações</b> sobre mim antes de começar. Use '
                                    '/info para isso.\n\n'
                                    'Além disso, você pode usar /cancel a qualquer momento caso sinta-se satisfeito e '
                                    'queira sair.\n\n'
                                    'Você está pronto? <b>Use /media para começarmos</b>.\n\n'
                                    '<b>Em caso de dúvidas, mande uma mensagem para: @lk_mzt</b>',
                                    parse_mode=telegram.constants.ParseMode.HTML)
    print(update.effective_user.id)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('<b>SOBRE MIM</b>\n\n'
                                    '1 - Para o computo da sua <b>média</b>, utilizo-me das métricas estabelecidas '
                                    'pelo edital. Desta forma, a nota que você verá aqui será fidedigna a que você '
                                    'verá no ranking oficial disponibilizado pela ESA.\n\n'
                                    '2 - O <b>ranking</b> é baseado nas notas de todos os candidatos que calcularam a '
                                    'sua nota aqui e não se importaram em compartilhá-la. Não se preocupe se você não '
                                    'se encontra entre a quantidade de vagas, lembre-se que se trata de uma estimativa '
                                    'que não leva em consideração a nota da redação e as fases seguintes que eliminam '
                                    'muitos candidatos.\n\n'
                                    '3 - Devido a limitações financeiras, ficarei <b>disponível até o dia 28 de '
                                    'novembro de 2022</b>.\n\n'
                                    '<b>Feito por @lk_mzt</b>', parse_mode=telegram.constants.ParseMode.HTML)


async def average(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    options = [[InlineKeyboardButton('Entendido', callback_data=str(CONFIRM))]]
    await update.message.reply_text('<b>ATENÇÃO!</b>\n\n'
                                    'Para que a sua média seja calculada corretamente, lembre-se de <b>considerar as '
                                    'questões anuladas como acertos</b>, assim como previsto no edital da ESA. \n\n'
                                    'Além disso, <b>preze pela integridade do ranking</b>, pois apenas em caso de '
                                    'sucesso esse sistema poderá ser implementado para outros concursos militares e '
                                    'mantido nos anos seguintes. \n\n'
                                    'Você está se preparando para a <b>carreira militar</b> e faz-se necessário que '
                                    'você aprenda a encarar as coisas relacionadas a ela com <b>seriedade</b>. '
                                    'Entendido, senhor(a)?',
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=options),
                                    parse_mode=telegram.constants.ParseMode.HTML)

    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.edit_message_reply_markup(reply_markup=None)

    await query.answer()

    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                       action=telegram.constants.ChatAction.TYPING)
    sleep(1)
    await query.message.reply_text('Em respeito aos demais candidatos, caso seja detectada qualquer incongruência nos '
                                   'dados fornecidos, você poderá ser <b>banido do sistema por tempo '
                                   'indeterminado</b>, sendo esta punição <b>irrevogável</b>. Portanto, <b>atente-se '
                                   'às informações prestadas</b>!\n\n'
                                   '<b>Obs:</b> Se em algum momento você notar que deu alguma informação errada, '
                                   '<b>utilize o /cancel para finalizar e o /media para recomeçar</b> pois você não '
                                   'poderá alterar essas informações depois.',
                                   parse_mode=telegram.constants.ParseMode.HTML)
    sleep(3)

    keyboard = [[KeyboardButton('Geral')], [KeyboardButton('Saúde')]]
    markup = ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder='Geral ou Saúde')

    await query.message.reply_text('Qual é a sua *ÁREA*?',
                                   reply_markup=markup,
                                   parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

    return SPECIALTY


async def get_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    specialty = update.message.text[0].upper()
    context.user_data['specialty'] = specialty

    if specialty == 'G':
        context.user_data['math_qtt'] = 14
        context.user_data['port_qtt'] = 14
        context.user_data['hgb_qtt'] = 12
        context.user_data['eng_qtt'] = 10

        await update.message.reply_text('Quantos acertos você obteve em *PORTUGUÊS*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
                                        reply_markup=ReplyKeyboardRemove())

        return PORT

    elif specialty == 'S':
        context.user_data['spec_qtt'] = 12
        context.user_data['math_qtt'] = 10
        context.user_data['port_qtt'] = 10
        context.user_data['hgb_qtt'] = 8
        context.user_data['eng_qtt'] = 10

        await update.message.reply_text('Quantos acertos você obteve em *CTE \\(Conhecimentos específicos\\)*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
                                        reply_markup=ReplyKeyboardRemove())

        return SPECIFIC

    else:
        await update.message.reply_text('Por favor, escolha uma das especialidades informadas!')


async def specific_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    spec = int(update.message.text)
    spec_qtt = int(context.user_data.get('spec_qtt'))

    if spec > spec_qtt:
        await update.message.reply_text('Quantidade de acertos inválida. Tente novamente...')
    else:
        context.user_data['spec'] = spec
        await update.message.reply_text('Quantos acertos você obteve em *PORTUGUÊS*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

        return PORT


async def portuguese_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    port = int(update.message.text)
    port_qtt = int(context.user_data.get('port_qtt'))

    if port > port_qtt:
        await update.message.reply_text('Quantidade de acertos inválida. Tente novamente...')
    else:
        context.user_data['port'] = port

        await update.message.reply_text('Quantos acertos você obteve em *MATEMÁTICA*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

        return MATH


async def mathmatics_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    math = int(update.message.text)
    math_qtt = int(context.user_data.get('math_qtt'))

    if math > math_qtt:
        await update.message.reply_text('Quantidade de acertos inválida. Tente novamente...')
    else:
        context.user_data['math'] = math

        await update.message.reply_text('Quantos acertos você obteve em *HISTÓRIA e GEOGRAFIA*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

        return HIST_GEO


async def hist_and_geo_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    hist_geo = int(update.message.text)
    hgb_qtt = int(context.user_data.get('hgb_qtt'))

    if hist_geo > hgb_qtt:
        await update.message.reply_text('Quantidade de acertos inválida. Tente novamente...')
    else:
        context.user_data['hist_geo'] = hist_geo

        await update.message.reply_text('Quantos acertos você obteve em *INGLÊS*?',
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

        return ENG


async def english_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                       action=telegram.constants.ChatAction.TYPING)
    eng = int(update.message.text)
    eng_qtt = int(context.user_data.get('eng_qtt'))

    if eng > eng_qtt:
        await update.message.reply_text('Quantidade de acertos inválida. Tente novamente...')
    else:
        context.user_data['eng'] = eng

        port_qtt = int(context.user_data.get('port_qtt'))
        math_qtt = int(context.user_data.get('math_qtt'))
        hgb_qtt = int(context.user_data.get('hgb_qtt'))
        eng_qtt = int(context.user_data.get('eng_qtt'))

        # Calculate candidate's average:
        port_avg = round(int(context.user_data.get('port')) * 10 / port_qtt, 3)
        math_avg = round(int(context.user_data.get('math')) * 10 / math_qtt, 3)
        hist_geo_avg = round(int(context.user_data.get('hist_geo')) * 10 / hgb_qtt, 3)
        eng_avg = round(int(context.user_data.get('eng')) * 10 / eng_qtt, 3)

        final_avg: float = 0

        specialty = "GERAL" if context.user_data.get('specialty') == 'G' else "SAÚDE"
        spec_text = ""
        spec_reply = ""

        if specialty == 'GERAL':
            final_avg = (port_avg + math_avg + hist_geo_avg + eng_avg) / 4
        elif specialty == 'SAÚDE':
            spec_qtt = int(context.user_data.get('spec_qtt'))
            spec_avg = int(context.user_data.get('spec')) * 10 / spec_qtt
            final_avg = (port_avg + math_avg + hist_geo_avg + eng_avg + 2 * spec_avg) / 6

            spec_text = f'**CTE:** {context.user_data.get("spec")}/{spec_qtt}\n'
            spec_reply = f'<b>CTE:</b> {context.user_data.get("spec")}/{spec_qtt}\n'
        #####
        keyboard = [
            [InlineKeyboardButton('Sim, por favor.', callback_data=str(CONFIRM))],
            [InlineKeyboardButton('Não, estou satisfeito.', callback_data=str(END))]
        ]

        text = (f'🇧🇷\n**Aproveitamento ESA 2022/2023 - {specialty}**\n\n'
                f'{spec_text}'
                f'**Português:** {context.user_data.get("port")}/{port_qtt}\n'
                f'**Matemática:** {context.user_data.get("math")}/{math_qtt}\n'
                f'**História e Geografia:** {context.user_data.get("hist_geo")}/{hgb_qtt}\n'
                f'**Inglês:** {context.user_data.get("eng")}/{eng_qtt}\n\n'
                f'**Média: {round(final_avg, 3)}**\n\n')

        share_keyboard = [[InlineKeyboardButton('Compartilhar', switch_inline_query=text)]]

        share_markup = InlineKeyboardMarkup(inline_keyboard=share_keyboard)

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await update.message.reply_text(f'<b>Aproveitamento ESA 2022/2023 - {specialty}</b>\n\n'
                                        f'{spec_reply}'
                                        f'<b>Português:</b> {context.user_data.get("port")}/{port_qtt}\n'
                                        f'<b>Matemática:</b> {context.user_data.get("math")}/{math_qtt}\n'
                                        f'<b>História e Geografia:</b> {context.user_data.get("hist_geo")}/{hgb_qtt}\n'
                                        f'<b>Inglês:</b> {context.user_data.get("eng")}/{eng_qtt}\n\n'
                                        f'<b>Média: {round(final_avg, 3)}</b>\n\n',
                                        parse_mode=telegram.constants.ParseMode.HTML,
                                        reply_markup=share_markup)

        sleep(3)

        await update.message.reply_text('Você gostaria de fazer parte do ranking de candidatos a ESA 2022/2023?',
                                        reply_markup=markup)


async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.edit_message_reply_markup(reply_markup=None)

    await query.answer()

    if repository.is_candidate_already_registered(user_id=update.effective_user.id):
        user_result: list = repository.get_candidate_result(user_id=update.effective_user.id)

        keyboard = [
            [InlineKeyboardButton('Sim', callback_data=str(EDIT))],
            [InlineKeyboardButton('Não', callback_data=str(END))]
        ]

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        user_specialty: str = user_result[0]

        specific = f'<b>CTE: {user_result[6]}</b>\n\n' if user_specialty == 'S' else ''

        await query.edit_message_text('Você já está cadastrado no ranking com o seguinte resultado: \n\n'
                                      f'{specific}'
                                      f'<b>Português:</b> {user_result[1]}\n'
                                      f'<b>Matemática:</b> {user_result[2]}\n'
                                      f'<b>História e Geografia:</b> {user_result[3]}\n'
                                      f'<b>Inglês:</b> {user_result[4]}\n\n'
                                      f'<b>Média: {user_result[5]}</b>\n\n'
                                      'Você gostaria de altera-lo para o resultado que você acabou de calcular?',
                                      parse_mode=telegram.constants.ParseMode.HTML,
                                      reply_markup=markup)

    else:
        await query.edit_message_text('Qual é o seu *PRIMEIRO NOME*?',
                                      parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
        return FIRST_NAME


async def edit_avg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.edit_message_reply_markup(reply_markup=None)

    await query.answer()

    specialty = context.user_data.get('specialty')

    port_qtt = int(context.user_data.get('port_qtt'))
    math_qtt = int(context.user_data.get('math_qtt'))
    hgb_qtt = int(context.user_data.get('hgb_qtt'))
    eng_qtt = int(context.user_data.get('eng_qtt'))

    port_avg = round(int(context.user_data.get('port')) * 10 / port_qtt, 3)
    math_avg = round(int(context.user_data.get('math')) * 10 / math_qtt, 3)
    hist_geo_avg = round(int(context.user_data.get('hist_geo')) * 10 / hgb_qtt, 3)
    eng_avg = round(int(context.user_data.get('eng')) * 10 / eng_qtt, 3)

    final_avg: float = 0

    if specialty == 'G':
        final_avg = round((port_avg + math_avg + hist_geo_avg + eng_avg) / 4, 3)

        repository.update_general_result(user_id=update.effective_user.id,
                                         port_avg=port_avg,
                                         math_avg=math_avg,
                                         hist_geo_avg=hist_geo_avg,
                                         eng_avg=eng_avg,
                                         final_avg=final_avg)

    elif specialty == 'S':
        specific_avg = round(int(context.user_data.get('spec')) * 10 / 12, 3)
        final_avg = round((port_avg + math_avg + hist_geo_avg + eng_avg + 2 * specific_avg) / 6, 3)

        repository.update_health_result(user_id=update.effective_user.id,
                                        port_avg=port_avg,
                                        math_avg=math_avg,
                                        hist_geo_avg=hist_geo_avg,
                                        eng_avg=eng_avg,
                                        specific_avg=specific_avg,
                                        final_avg=final_avg)

    await query.message.reply_text(f'<b>Sua média foi alterada para {final_avg} com sucesso!</b>',
                                   parse_mode=telegram.constants.ParseMode.HTML)


async def first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer: str = update.message.text.strip()

    if re.search(r_name, answer):
        context.user_data['first_name'] = answer
        await update.message.reply_text("Qual é o seu *SOBRENOME*?",
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
        return LAST_NAME

    else:
        await update.message.reply_text('Por favor, digite um nome válido.')


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer: str = update.message.text.strip()

    if re.search(r_name, answer):
        context.user_data['last_name'] = answer
        reply_keyboard = [[KeyboardButton('Masculino')], [KeyboardButton('Feminino')]]
        reply_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,
                                           one_time_keyboard=True,
                                           input_field_placeholder='Masculino ou Feminino')
        await update.message.reply_text("Qual é o seu *SEXO*?",
                                        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
                                        reply_markup=reply_markup)
        return GENDER
    else:
        await update.message.reply_text('Por favor, digite um nome válido.')


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gender'] = update.message.text[0].upper()

    await update.message.reply_text('Qual é a sua <b>DATA DE NASCIMENTO</b>? \n\n'
                                    '- A data deve estar no padrão <b>DD/MM/AAAA</b>',
                                    parse_mode=telegram.constants.ParseMode.HTML,
                                    reply_markup=ReplyKeyboardRemove())

    return BIRTH_DATE


async def get_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Checar se é uma data válida
    try:
        birth = datetime.strptime(update.message.text.strip(), '%d/%m/%Y').date()
        current_year = date.today().year

        specialty = context.user_data.get('specialty')
        age_at_enrollment = current_year + 1 - birth.year

        # Checar se a idade do usuário atende aos requisitos de idade da especialidade
        valid_general_candidate = specialty == 'G' and 17 <= age_at_enrollment <= 24
        valid_health_candidate = specialty == 'S' and 17 <= age_at_enrollment <= 26

        if valid_general_candidate or valid_health_candidate:
            context.user_data['birth'] = birth

            keyboard = [[KeyboardButton('Ampla')], [KeyboardButton('Cota')]]
            markup = ReplyKeyboardMarkup(keyboard=keyboard,
                                         one_time_keyboard=True,
                                         input_field_placeholder='Ampla ou Cota?')
            await update.message.reply_text('Para quais vagas você está concorrendo?', reply_markup=markup)

            return VACANCY_TYPE
        else:
            await update.message.reply_text('Você não atende aos requisitos de idade impostos pela ESA.')
            await cancel(update, context)

    except ValueError:
        await update.message.reply_text('Por favor, digite uma data válida no formato <b>DD/MM/AAAA</b>.',
                                        parse_mode=telegram.constants.ParseMode.HTML)


async def vacancy_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Aguarde enquanto ajustamos as coisas...')

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)

    vacancy = update.message.text
    context.user_data['vacancy'] = vacancy

    repository.create_candidate(
        user_id=update.effective_user.id,
        name=context.user_data.get('first_name').title() + " " + context.user_data.get('last_name').title(),
        gender=context.user_data.get('gender'),
        birth=context.user_data.get('birth'),
        is_quota_holder=True if vacancy == 'Cota' else False,
        specialty=context.user_data.get('specialty')
    )

    specialty: str = context.user_data.get('specialty')

    port_qtt = int(context.user_data.get('port_qtt'))
    math_qtt = int(context.user_data.get('math_qtt'))
    hgb_qtt = int(context.user_data.get('hgb_qtt'))
    eng_qtt = int(context.user_data.get('eng_qtt'))

    port_avg = round(int(context.user_data.get('port')) * 10 / port_qtt, 3)
    math_avg = round(int(context.user_data.get('math')) * 10 / math_qtt, 3)
    hist_geo_avg = round(int(context.user_data.get('hist_geo')) * 10 / hgb_qtt, 3)
    eng_avg = round(int(context.user_data.get('eng')) * 10 / eng_qtt, 3)

    if specialty == 'G':
        final_avg = round((port_avg + math_avg + hist_geo_avg + eng_avg) / 4, 3)
        repository.create_general_result(user_id=update.effective_user.id, port_avg=port_avg, math_avg=math_avg,
                                         hist_geo_avg=hist_geo_avg, eng_avg=eng_avg, final_avg=final_avg)
    elif specialty == 'S':
        specific_avg = round(int(context.user_data.get('spec')) * 10 / 12, 3)
        final_avg = round((port_avg + math_avg + hist_geo_avg + eng_avg + 2 * specific_avg) / 6, 3)
        repository.create_health_result(user_id=update.effective_user.id, port_avg=port_avg, math_avg=math_avg,
                                        hist_geo_avg=hist_geo_avg, eng_avg=eng_avg, specific_avg=specific_avg,
                                        final_avg=final_avg)

    await update.message.reply_text('Você foi cadastrado com sucesso no ranking que será divulgado diariamente '
                                    'no canal: https://t.me/+VIcsXvbqkH9jMjdh')

    await cancel(update, context)


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    await query.message.reply_text('Foi um prazer ajudá-lo. Compartilhe-me com mais candidatos para nos '
                                   'aproximarmos ao máximo do ranking final da ESA 2022/2023. \n\nFé na missão! '
                                   '🇧🇷')

    context.user_data.clear()
    context.application.drop_user_data(user_id=update.effective_user.id)

    context.chat_data.clear()
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Foi um prazer ajudá-lo. Compartilhe-me com mais candidatos para nos '
                                    'aproximarmos ao máximo do ranking final da ESA 2022/2023. \n\nFé na missão! '
                                    '🇧🇷', reply_markup=ReplyKeyboardRemove())

    context.user_data.clear()
    context.application.drop_user_data(user_id=update.effective_user.id)

    context.chat_data.clear()
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()

    return ConversationHandler.END


async def generate_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != os.getenv('ADMIN_ID'):
        print("Sem permissão")
        return
    pandas.options.display.float_format = '{:.3f}'.format
    pandas.set_option('display.width', 1000)
    pandas.set_option('colheader_justify', 'center')

    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                       action=telegram.constants.ChatAction.UPLOAD_DOCUMENT)

    generate_men_ranking_pdf()
    generate_woman_ranking_pdf()
    generate_health_ranking_pdf()
    generate_quota_men_ranking_pdf()
    generate_quota_woman_ranking_pdf()

    current_time = datetime.now()
    await update.message.reply_text(f'<b>Atualização {current_time.day}/{current_time.month}/{current_time.year} '
                                    f'{current_time.hour}:{current_time.minute}</b>',
                                    parse_mode=telegram.constants.ParseMode.HTML)

    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open('ranking_ampla_masculino.pdf', 'rb'))
    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open('ranking_ampla_feminino.pdf', 'rb'))
    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open('ranking_cota_masculino.pdf', 'rb'))
    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open('ranking_cota_feminino.pdf', 'rb'))
    await context.bot.send_document(chat_id=update.effective_message.chat_id,
                                    document=open('ranking_saude.pdf', 'rb'))

    os.remove('ranking_ampla_masculino.html')
    os.remove('ranking_ampla_masculino.pdf')
    os.remove('ranking_ampla_feminino.html')
    os.remove('ranking_ampla_feminino.pdf')
    os.remove('ranking_cota_masculino.html')
    os.remove('ranking_cota_masculino.pdf')
    os.remove('ranking_cota_feminino.html')
    os.remove('ranking_cota_feminino.pdf')
    os.remove('ranking_saude.html')
    os.remove('ranking_saude.pdf')


def generate_men_ranking_pdf():
    df = pandas.DataFrame(repository.get_general_men_ranking(),
                          columns=['Nome', 'Média', 'Port', 'Mat', 'Hist/Geo', 'Ing', 'Nascimento', 'Cotista'])

    df.insert(0, 'Class', df.index + 1)
    df['Nome'] = df['Nome'].str.upper()

    html_main_structure = '''
    <html>
      <head><title>Ranking ESA 2022/2023 Area Geral Masculino</title></head>
      <link rel="stylesheet" type="text/css" href="df_style.css"/>
      <meta charset="UTF-8">
      <body>
        {table}
      </body>
    </html>
    '''

    with open("ranking_ampla_masculino.html", "w", encoding="utf-8") as file:
        file.write(html_main_structure.format(table=df.to_html(index=False)))
    options = {
        "enable-local-file-access": None,
        'encoding': "UTF-8"
    }
    pdfkit.from_file(input='ranking_ampla_masculino.html', css='df_style.css',
                     output_path='ranking_ampla_masculino.pdf', options=options)


def generate_woman_ranking_pdf():
    df = pandas.DataFrame(repository.get_general_woman_result(),
                          columns=['Nome', 'Média', 'Port', 'Mat', 'Hist/Geo', 'Ing', 'Nascimento', 'Cotista'])

    df.insert(0, 'Class', df.index + 1)
    df['Nome'] = df['Nome'].str.upper()

    html_main_structure = '''
    <html>
      <head><title>Ranking ESA 2022/2023 Area Geral Feminino</title></head>
      <link rel="stylesheet" type="text/css" href="df_style.css"/>
      <meta charset="UTF-8">
      <body>
        {table}
      </body>
    </html>
    '''

    with open("ranking_ampla_feminino.html", "w", encoding="utf-8") as file:
        file.write(html_main_structure.format(table=df.to_html(index=False)))
    options = {
        "enable-local-file-access": None,
        'encoding': "UTF-8"
    }
    pdfkit.from_file(input='ranking_ampla_feminino.html', css='df_style.css', output_path='ranking_ampla_feminino.pdf',
                     options=options)


def generate_quota_men_ranking_pdf() -> None:
    df = pandas.DataFrame(repository.get_general_quota_men_result(),
                          columns=['Nome', 'Média', 'Port', 'Mat', 'Hist/Geo', 'Ing', 'Nascimento', 'Cotista'])

    df.insert(0, 'Class', df.index + 1)
    df['Nome'] = df['Nome'].str.upper()

    html_main_structure = '''
        <html>
          <head><title>Ranking ESA 2022/2023 Area Geral Masculino Cota</title></head>
          <link rel="stylesheet" type="text/css" href="df_style.css"/>
          <meta charset="UTF-8">
          <body>
            {table}
          </body>
        </html>
        '''

    with open("ranking_cota_masculino.html", "w", encoding="utf-8") as file:
        file.write(html_main_structure.format(table=df.to_html(index=False)))
    options = {
        "enable-local-file-access": None,
        'encoding': "UTF-8"
    }
    pdfkit.from_file(input='ranking_cota_masculino.html', css='df_style.css', output_path='ranking_cota_masculino.pdf',
                     options=options)


def generate_quota_woman_ranking_pdf() -> None:
    df = pandas.DataFrame(repository.get_general_quota_woman_result(),
                          columns=['Nome', 'Média', 'Port', 'Mat', 'Hist/Geo', 'Ing', 'Nascimento', 'Cotista'])

    df.insert(0, 'Class', df.index + 1)
    df['Nome'] = df['Nome'].str.upper()

    html_main_structure = '''
        <html>
          <head><title>Ranking ESA 2022/2023 Area Geral Feminino Cota</title></head>
          <link rel="stylesheet" type="text/css" href="df_style.css"/>
          <meta charset="UTF-8">
          <body>
            {table}
          </body>
        </html>
        '''

    with open("ranking_cota_feminino.html", "w", encoding="utf-8") as file:
        file.write(html_main_structure.format(table=df.to_html(index=False)))
    options = {
        "enable-local-file-access": None,
        'encoding': "UTF-8"
    }
    pdfkit.from_file(input='ranking_cota_feminino.html', css='df_style.css', output_path='ranking_cota_feminino.pdf',
                     options=options)


def generate_health_ranking_pdf():
    df = pandas.DataFrame(repository.get_health_result(),
                          columns=['Nome', 'Média', 'CTE', 'Port', 'Mat', 'Hist/Geo', 'Ing', 'Nascimento', 'Cotista'])

    df.insert(0, 'Class', df.index + 1)
    df['Nome'] = df['Nome'].str.upper()

    html_main_structure = '''
    <html>
      <head><title>Ranking ESA 2022/2023 Saúde</title></head>
      <link rel="stylesheet" type="text/css" href="df_style.css"/>
      <meta charset="UTF-8">
      <body>
        {table}
      </body>
    </html>
    '''

    with open("ranking_saude.html", "w", encoding="utf-8") as file:
        file.write(html_main_structure.format(table=df.to_html(index=False)))
    options = {
        "enable-local-file-access": None,
        'encoding': "UTF-8"
    }
    pdfkit.from_file(input='ranking_saude.html', css='df_style.css', output_path='ranking_saude.pdf', options=options)


def main() -> None:
    load_dotenv()
    application = Application.builder().token(os.getenv('API_KEY')).build()

    score_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("media", average)],
        states={
            CONFIRM: [CallbackQueryHandler(confirm, pattern="^" + str(CONFIRM) + "$")],
            SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_specialty)],
            SPECIFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, specific_score)],
            MATH: [MessageHandler(filters.TEXT & ~filters.COMMAND, mathmatics_score)],
            PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, portuguese_score)],
            HIST_GEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, hist_and_geo_score)],
            ENG: [MessageHandler(filters.TEXT & ~filters.COMMAND, english_score)],
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birth_date)],
            VACANCY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, vacancy_type)],
        },
        fallbacks=[
            CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
            CallbackQueryHandler(ranking, pattern="^" + str(CONFIRM) + "$"),
            CallbackQueryHandler(edit_avg, pattern="^" + str(EDIT) + "$"),
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True
    )

    application.add_handler(score_conv_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("generate_ranking", generate_ranking))

    application.run_polling()


if __name__ == "__main__":
    main()
