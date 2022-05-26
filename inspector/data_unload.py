from app import db
from models import User, Pokaz, Counter, House, Address
from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime
from utils import month_name
import os


class DataUploader():

    def __init__(self,
                 type: int,
                 mkdid: int = None,
                 kvid: int = None,
                 personid: int = None,
                 period_start: dict = None,
                 period_end: dict = None,
                 user_id: int = None):
        self.__filename = 'unloads/Выгрузка_{}_{}.xlsx'.format(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"), user_id)
        self.__user = user_id
        self.mkd_id = mkdid
        self.kv_id = kvid
        self.person_id = personid
        self.type = type
        self.__wb = Workbook()
        self.__ws = self.__wb.active
        self.__ws.title = 'Выгрузка'
        self.period_start_m = period_start['m']
        self.period_end_m = period_end['m']
        self.period_start_y = period_start['y']
        self.period_end_y = period_end['y']
        self.__row = 0
        self.__col = 0

        self.font_bold = Font(name='Arial', size=12, bold=True)
        self.font_regular = Font(name='Arial', size=12)

        self.__cell_filter = 'B6'
        self.__prepareBookHeader()

    def __prepareBookHeader(self):
        cell_sysname = 'A1'
        cell_title = 'A3'
        cell_title_end = 'C3'
        cell_type = 'A4'
        cell_type_in = 'B4'
        cell_date = 'A5'
        cell_date_in = 'B5'
        cell_date_end = 'D5'
        cell_filter_param = 'A6'
        cell_filter_end = 'H6'

        self.__ws[cell_sysname].font = self.font_bold
        self.__ws[cell_title].font = self.font_bold
        self.__ws[cell_type].font = self.font_bold
        self.__ws[cell_type_in].font = self.font_regular
        self.__ws[cell_date].font = self.font_bold
        self.__ws[cell_date_in].font = self.font_regular
        self.__ws[cell_filter_param].font = self.font_bold
        self.__ws[self.__cell_filter].font = self.font_regular

        self.__ws[cell_sysname] = 'АСУПСКУ'
        self.__ws[cell_title] = 'Выгрузка показаний приборов учета'
        self.__ws[cell_date] = 'Дата:'
        self.__ws[cell_date_in] = datetime.now()
        self.__ws[cell_type] = 'Отбор:'
        self.__ws[cell_type_in] = self.__getOtborName()
        self.__ws[cell_date] = 'Дата'
        self.__ws[cell_date_in] = datetime.now().strftime('%d.%m.%Y (%H:%M:%S)')
        self.__ws[cell_filter_param] = 'Фильтр:'
        self.__ws.merge_cells('{}:{}'.format(cell_date_in, cell_date_end))
        self.__ws.merge_cells('{}:{}'.format(self.__cell_filter, cell_filter_end))
        self.__ws.merge_cells('{}:{}'.format(cell_title,cell_title_end))

        self.__row = 9
        self.__col = 1

    def __getOtborName(self):
        if self.type == 1:
            return 'По МКД'
        elif self.type == 2:
            return 'По квартире'
        elif self.type == 3:
            return 'По пользователю'

    def __getFilterName(self):
        if self.type == 1:
            return 'МКД'
        elif self.type == 2:
            return 'Квартира'
        elif self.type == 3:
            return 'Пользователь'

    def __getUnloadFlat(self):
        flat = self.kv_id
        flat_info = Address.query.filter_by(id=flat).limit(1).first()
        flat_adr = flat_info.get_full_address()
        self.__ws[self.__cell_filter] = self.__getFilterName() + ' ' + flat_adr
        self.__prepareUnloadDataTable()
        flat_counters = db.session.query(Counter.name, Counter.id).filter_by(flat = flat_info.id).all()
        for c in flat_counters:
            pokaz_data = Pokaz.query.filter(Pokaz.counter == c.id,
                                            Pokaz.p_month >= self.period_start_m,
                                            Pokaz.p_year >= self.period_start_y,
                                            Pokaz.p_month <= self.period_end_m,
                                            Pokaz.p_year <= self.period_end_y).order_by(Pokaz.id.desc()).all()
            for p in pokaz_data:
                column = 1
                self.__ws.cell(row=self.__row, column=column, value=c.name)
                column += 1
                self.__ws.cell(row=self.__row, column=column, value='{} {}'.format(month_name(p.p_month),p.p_year))
                column += 1
                self.__ws.cell(row=self.__row, column=column, value=p.amount)
                column += 1
                self.__ws.cell(row=self.__row, column=column, value=p.added_on)
                column += 1
                added_user = db.session.query(User.name).filter_by(id=p.added_by).limit(1).first()
                user_name = added_user.name if added_user else 'Неизвестно'
                self.__ws.cell(row=self.__row, column=column, value=user_name)
                self.__row += 1

    def __prepareUnloadDataTable(self):
        # верхняя строка таблицы
        column = self.__col
        self.__ws.cell(row=self.__row, column=column, value='Прибор учета').font = self.font_bold
        column += 1
        self.__ws.cell(row=self.__row, column=column, value='Период').font = self.font_bold
        column += 1
        self.__ws.cell(row=self.__row, column=column, value='Показания').font = self.font_bold
        column += 1
        self.__ws.cell(row=self.__row, column=column, value='Дата передачи').font = self.font_bold
        column += 1
        self.__ws.cell(row=self.__row, column=column, value='Кем переданы').font = self.font_bold
        self.__row += 1

    def __add_bottom(self):
        self.__row += 3
        user = db.session.query(User.name).filter_by(id=self.__user).limit(1).first()
        self.__ws.cell(row=self.__row, column=1, value='Выгрузку запросил: инспектор {}'.format(user.name))

    def __prettify(self):
        for column_cells in self.__ws.columns:
            unmerged_cells = list(
                filter(lambda cell_to_check: cell_to_check.coordinate not in self.__ws.merged_cells, column_cells))
            length = max(len(str(cell.value)) for cell in unmerged_cells)
            self.__ws.column_dimensions[unmerged_cells[0].column_letter].width = length * 1.5

    def unload_and_save(self):
        if self.type == 2:
            self.__getUnloadFlat()
        self.__prettify()
        self.__add_bottom()
        self.__save_unload()
        return os.path.abspath(self.__filename)

    def __save_unload(self):
        return self.__wb.save(self.__filename)
