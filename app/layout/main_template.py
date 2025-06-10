from db.data import PRAYER_TIMES
from components.navigation import TopNav
from components.page import AppContainer
from components.cards import homepage_card
from fasthtml.common import RedirectResponse
from components.cards import prayer_times_page
from fasthtml.components import H1, H2, Div, Img, P, Span, Grid, A, Ul, Li

def get_main_routes(rt):
    # @rt('/')
    # def get():
    #     return AppContainer(
    #                 Div(
    #                     Div (
    #                         Div(alt='Conference banner_2', cls='hero-image'),
    #                         Div(
    #                             Div(
    #                                 Img(src='mas-logo-square.png', alt='MAS Logo', cls='logo'),
    #                                 Div( 
    #                                     H1('2nd Annual CYP Conference', cls='h3'),
    #                                     P('Mover and Shakers in Islam: Transformative Traits'),
    #                                     cls='logo-text-text'  
    #                                 ),
    #                                 cls='card card-side logo-text'
    #                             ),
    #                             Div(
    #                                 Span(
    #                                     Img(src='location.png', alt='location icon', cls='hero-icon'),
    #                                     P('1515 Blake Dr, Richardson'),
    #                                     cls='flex items-center justify-between',
    #                                 ),
    #                                 Span(
    #                                     Img(src='calendar.png', alt='calendar icon', cls='hero-icon'),
    #                                     P('Oct 12, 2024'),
    #                                     cls='flex items-center justify-between',
    #                                 ),
    #                                 cls='flex items-center justify-between location-date'
    #                             ),
    #                             cls='conference-info'
    #                         ),
    #                         Grid(
    #                             homepage_card(icon_name='about.svg', title='About', card_color='blue', href='/about', cls='full-card'),
    #                             homepage_card(icon_name='prayer.svg', title='Prayer Times', card_color='green', href='/prayer-times', cls='full-card'),
    #                             homepage_card(icon_name='chat.svg', title='Q&A', card_color='pink', href='/qa', cls='full-card'),
    #                             homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color='pink', href='/feedback-survey', cls='full-card'),
    #                         cls='grid card-grid mb-7 home-page-content'),
    #                         homepage_card(
    #                             icon_name='registration.svg', title='Registration', card_color='blue', href='/registration',
    #                             cls='mx-6 mt-4'
    #                                       ),
    #                         cls='mb-8',
    #                         ),
    #                     cls='container mx-auto',
    #                     id='page-content',
    #                 ),
    #                 active_button_index=1
    #             )
    
    @rt('/')
    def get():
        return AppContainer(
                    Div(
                        Div (
                            Div(alt='Conference banner_2', cls='hero-image cropped'),
                            Div(
                                Div(
                                    Img(src='mas-logo-square.png', alt='MAS Logo', cls='logo'),
                                    Div( 
                                        H1('2nd Annual CYP Conference', cls='h3'),
                                        P('Mover and Shakers in Islam: Transformative Traits'),
                                        cls='logo-text-text'  
                                    ),
                                    cls='card card-side logo-text'
                                ),
                                Div(
                                    Span(
                                        Img(src='location.png', alt='location icon', cls='hero-icon'),
                                        P('5353 Independence Pkwy, Frisco'),
                                        cls='flex items-center justify-between',
                                    ),
                                    Span(
                                        Img(src='calendar.png', alt='calendar icon', cls='hero-icon'),
                                        P('Oct 12, 2024'),
                                        cls='flex items-center justify-between',
                                    ),
                                    cls='flex items-center justify-between location-date'
                                ),
                                cls='conference-info'
                            ),
                            Grid(
                                homepage_card(icon_name='about.svg', title='About', card_color='blue', href='/about', cls='full-card'),
                                homepage_card(icon_name='prayer.svg', title='Prayer Times', card_color='green', href='/prayer-times', cls='full-card'),
                                homepage_card(icon_name='chat.svg', title='Q&A', card_color='pink', href='/qa', cls='full-card'),
                                homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color='pink', href='/feedback-survey', cls='full-card'),
                            cls='grid card-grid mb-7 home-page-content'),
                            homepage_card(
                                icon_name='registration.svg', title='Registration', card_color='blue', href='/registration',
                                cls='mx-6 mt-4'
                                          ),
                            cls='mb-8',
                            ),
                        cls='container mx-auto',
                        id='page-content',
                    ),
                    active_button_index=1
                )
    
    @rt('/about')
    def get():
        bulletPoints = [
            'Join us on a journey to uncover the driving forces behind the movers and shakers of our time, and discover how their transformative traits are reshaping our collective future.', 
            'We delve into the defining characteristics of a generation at the forefront of change.',
            'GAZA Teaching Us: Change is the product of sustained efforts of movers and shakers.',
            'Showcasing how young movers and shakers navigate challenges, challenge  norms, and champion progress.',
            'A testament to the continuous legacy of youth-driven change and the transformative power of visionary young leadership within the Islamic tradition.'
        ]
        return AppContainer(
            Div(
                TopNav('About',),
                Div(alt='Conference banner_2', cls='hero-image'),
                Div(
                    H2('Description' , cls='font-bold pb-2'),
                    Ul(
                        *[Li(point) for point in bulletPoints],
                        cls='text-sm about-list'
                    ),
                    cls='p-8',
                    ),
                id='page-content',
            ),
            active_button_index=1
        )