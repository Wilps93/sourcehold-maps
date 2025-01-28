import struct

from sourcehold.structure_tools.Buffer import Buffer
from sourcehold.iotools import unpack


from PIL import Image, ImageDraw

from sourcehold import palette



def cut_strict(data, type, rows):
    data = Buffer(data)
    if type.__class__ == int:
        type = type + "B"
    size = struct.calcsize(type)
    header = data.read(size * 2)

    headers = set()
    footers = set()

    # if header not in headers:
    #     print("header: {}".format(header))
    #     headers.add(header)

    chunks = []

    for i in range(0, rows + 1, 1):
        header = data.read(size * 2)

        # if header not in headers:
        #     print("header: {}".format(header))
        #     headers.add(header)

        chunk = [unpack(type, data.read(size)) for v in range(i * 2)]
        chunks.append(chunk)
        footer = data.read(size * 2)

        # if footer not in footers:
        #     print("footer: {}".format(footer))
        #     footers.add(footer)

    for i in range(rows, -1, -1):
        header = data.read(size * 2)

        # if header not in headers:
        #     print("header: {}".format(header))
        #     headers.add(header)

        chunk = [unpack(type, data.read(size)) for v in range(i * 2)]
        chunks.append(chunk)
        footer = data.read(size * 2)

        # if footer not in footers:
        #     print("footer: {}".format(footer))
        #     footers.add(footer)

    footer = data.read(size * 2)

    # if footer not in footers:
    #     print("footer: {}".format(footer))
    #     footers.add(footer)

    assert data.remaining() == 0

    return chunks[1:-1]


def cut(data, type, rows):
    data = Buffer(data)
    # if type.__class__ == int:
    #     type = type + "B"
    import re
    p = re.compile('[0-9]')
    t = re.compile('[A-Za-z]')
    size = struct.calcsize(type)
    number = 0
    if len(p.findall(type)) > 0:
        number = p.findall(type)[0]
        type = t.findall(type)[0]
    header = data.read(size * 2)

    chunks = []

    for i in range(0, rows + 1, 1):
        header = data.read(size * 2)
        chunk = [unpack(type, data.read(size), number) for v in range(i * 2)]
        chunks.append(chunk)
        footer = data.read(size * 2)

    for i in range(rows, -1, -1):
        header = data.read(size * 2)
        chunk = [unpack(type, data.read(size), number) for v in range(i * 2)]
        chunks.append(chunk)
        footer = data.read(size * 2)

    footer = data.read(size * 2)

    assert data.remaining() == 0

    return chunks[1:-1]


# Only applies when rows is even.

def translate_diamond_to_checkerboard(data):
    sq1 = data

    rows = len(sq1)

    assert rows % 2 == 0

    cutpoint = rows // 2

    width = rows
    height = rows

    out = []
    for i in range(width + 1):
        col = []
        for j in range(height + 1):
            col.append(None)
        out.append(col)

    for i in range(len(sq1)):
        for j in range(len(sq1[i])):
            ti, tj = iso_xy_to_image_xy((i, j), rows)
            out[width - ti][tj] = sq1[i][j]

    return out


def create_image(data1, palette):
    sq1 = data1

    rows = len(sq1)

    assert rows % 2 == 0

    cutpoint = rows // 2

    width = rows
    height = rows

    from PIL import Image, ImageColor
    im = Image.new('RGB', (width + 1, height + 1), ImageColor.getcolor('black', 'RGB'))

    for i in range(len(sq1)):
        for j in range(len(sq1[i])):
            ti, tj = iso_xy_to_image_xy((i, j), rows)
            im.putpixel((width - ti, tj), palette(sq1[i][j]))

    return im


def create_comparison_image(data1, data2):
    sq1 = data1
    sq2 = data2

    rows = len(sq1)

    assert rows % 2 == 0

    cutpoint = rows // 2

    width = rows
    height = rows

    from PIL import Image, ImageColor
    im = Image.new('RGB', (width + 1, height + 1), ImageColor.getcolor('black', 'RGB'))

    for i in range(len(sq1)):
        for j in range(len(sq1[i])):
            ti, tj = iso_xy_to_image_xy((i, j), rows)
            if sq1[i][j] != sq2[i][j]:
                im.putpixel((width - ti, tj), ImageColor.getcolor('red', 'RGB'))
            else:
                im.putpixel((width - ti, tj), ImageColor.getcolor('white', 'RGB'))

    return im


def interpret(data, type, opening, closing):
    buf = Buffer(data)
    depth = 0

    chunks = []

    chunk = b''

    while buf.remaining() >= max(len(opening), len(closing)):

        if buf.peek(len(opening)) == opening:
            depth += 1
            chunk = b''
            buf.read(len(opening))
        elif buf.peek(len(closing)) == closing:
            depth -= 1
            chunks.append(chunk)
            buf.read(len(closing))
        else:
            chunk += buf.read(1)

    mapdata = []

    s = struct.calcsize(type)

    for c in chunks:
        if len(c) == 0:
            continue

        buf = Buffer(c)
        ints = []
        while True:
            ints.append(struct.unpack(type, buf.read(s))[0])

            if buf.remaining() >= s:
                continue
            elif buf.remaining() == 0:
                break
            else:
                raise Exception("data left in buffer of size {}".format(buf.remaining()))

        mapdata.append(ints)

    return mapdata


def iso_xy_to_image_xy(coord, rows):
    assert rows % 2 == 0

    cut = rows // 2

    x = coord[0]
    y = coord[1]

    if x < cut:
        tx = (x * 2) + 1 - y
    else:
        tx = rows - y

    if x < cut:
        ty = y
    else:
        ty = (x - cut) * 2 + 1 + y

    return (tx, ty)


class TileLocationTranslator(object):

    def __init__(self, square_width=400):
        import math

        self.size = square_width

        size = square_width
        n_serialized_tiles = (2*((size/2)*((size/2)+1)))

        class Point(object):

            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

            def __repr__(self):
                return "{}<{}>".format(self.__class__.__name__, ",".join("{}={}".format(key, value) for key, value in self.__dict__.items()))

        class SerializedPoint(Point):

            def __init__(self, i, j):
                super().__init__(i=i, j=j)

            def to_tile_index(self):
                if self.i < size//2:
                    return TileIndex((self.i*(self.i+1)) + self.j)
                else:
                    return TileIndex((n_serialized_tiles - ((size - self.i)*(size-self.i+1))) + self.j)

            def to_square_index(self):
                if self.i < size/2:
                    return SquareIndex(((size/2)-1-self.i) + (self.i*size) + self.j)
                else:
                    return SquareIndex((-(size/2)+0+self.i) + (self.i*size) + self.j)

        class TileIndex(Point):

            def __init__(self, index):
                super().__init__(index=index)

            def to_serialized_point(self):
                if self.index < n_serialized_tiles/2:
                    i = math.floor(0.5 * ((math.sqrt((4 * self.index) + 1)) - 1))
                else:
                    i = math.floor(size - (0.5 * ((math.sqrt((4 * ((2 * ((size / 2) * ((size / 2) + 1))) - self.index)) + 1)) - 1)))

                index = SerializedPoint(i, 0).to_tile_index().index
                j = self.index - index

                return SerializedPoint(i, j)

        class SquareIndex(Point):

            def __init__(self, index):
                super().__init__(index=index)

            def to_serialized_point(self):
                i = math.floor(self.index / size)
                if i < size/2:
                    j = (self.index % size)-((size/2)-i-1)
                else:
                    j = (self.index % size) - (-(size/2)+0+i)
                return SerializedPoint(i, j)

            def to_square_point(self):
                i = math.floor(self.index / size)
                j = math.floor(self.index % size)
                return SquarePoint(i, j)

        class SquarePoint(Point):

            def __init__(self, i, j):
                super().__init__(i=i, j=j)

            def to_square_index(self):
                return SquareIndex(index=(size*self.i) + self.j)

        self.SquareIndex = SquareIndex
        self.SquarePoint = SquarePoint
        self.TileIndex = TileIndex
        self.SerializedPoint = SerializedPoint


class TileIndexTranslator(object):

    def __init__(self, square_size = 400):
        self.square_size = square_size

    def translate_file_index_to_game_tile_index(self, i, j=None):
        if j is None:
            i, j = i
        if i < (self.square_size / 2):
            return ((self.square_size / 2) - 1 - i) + (i * self.square_size) + j
        else:
            return (-(self.square_size / 2) + 0 + i) + (i * self.square_size) + j

    def translate_game_tile_index_to_file_index(self, index):
        i = index//self.square_size
        if i < (self.square_size / 2):
            j = (index % self.square_size) - ((self.square_size / 2) - i - 1)
        else:
            j = (index % self.square_size) - (-(self.square_size/2) + 0 + i)
        return i, j




class Point(object):

    def __init__(self, i, j):
        self.i = i
        self.j = j

    def __repr__(self):
        return "<{}>({}, {})".format(type(self).__name__, self.i, self.j)


class ScreenPoint(Point):

    def __init__(self, i, j, tile_width, tile_height):
        super().__init__(i, j)
        self.tile_width = tile_width
        self.tile_height = tile_height

    def translate_to_file_point(self):
        screen_width = int(400 * self.tile_width * 0.5)
        i = screen_width - self.i
        j = self.j
        i, j = (i // (self.tile_width // 2), j // (self.tile_height // 2))
        # TODO: inverse of staggering
        raise NotImplementedError()
        return FilePoint(i, j)

    def get_tile_points(self):
        return [(self.i, self.j),
                ((self.i + self.tile_width // 2), self.j + self.tile_height // 2),
                (self.i, self.j + self.tile_height),
                ((self.i - self.tile_width // 2), self.j + self.tile_height // 2)]


class GamePoint(Point):

    def __init__(self, i, j):
        super().__init__(i, j)

    def translate_to_file_point(self):
        return FilePoint(self.i, self.j - (abs(199-self.i) if self.i < 200 else abs(200-self.i)))

    def translate_to_screen_point(self, tile_width=32, tile_height=16):
        screen_width = int(400 * tile_width * 0.5)
        txi = self.i * (tile_width // 2)
        tyi = self.i * (tile_height // 2)
        txj = -1 * self.j * (tile_width // 2)
        tyj = self.j * (tile_height // 2)

        return ScreenPoint(screen_width - (txi + txj), tyi + tyj, tile_width, tile_height)


class FilePoint(Point):

    def __init__(self, i, j):
        super().__init__(i, j)

    def translate_to_game_index(self):
        size = 400
        if self.i < 200:
            return (self.i * (self.i + 1)) + self.j
        else:
            return (2 * (200 * (200 + 1))) - ((400 - self.i) * (400 - self.i + 1)) + self.j

    def translate_to_game_point(self):
        return GamePoint(self.i, self.j + (abs(199-self.i) if self.i < 200 else abs(200-self.i)))

    def _to_staggered(self):
        rows = 400

        cut = rows // 2

        x, y = (self.i, self.j)

        if x < cut:
            tx = (x * 2) + 1 - y
        else:
            tx = rows - y

        if x < cut:
            ty = y
        else:
            ty = (x - cut) * 2 + 1 + y

        return tx, ty

    def translate_to_screen_point(self, tile_width=32, tile_height=16):
        i, j = self._to_staggered()

        screen_width = None
        if screen_width is None:
            screen_width = int(400 * tile_width * 0.5)

        i, j = (i * (tile_width // 2), j * (tile_height // 2))

        xoff = i + 0
        yoff = j + 0
        #width = tile_width
        #height = tile_height

        return ScreenPoint(screen_width-xoff, yoff, tile_width, tile_height)
        #return [(screen_width-xoff, yoff), (screen_width-(xoff + width // 2), yoff + height // 2), (screen_width-xoff, yoff + height),
        #        (screen_width-(xoff - width // 2), yoff + height // 2)]




class DiamondSystem(object):

    def __init__(self, rows=400):
        if not rows % 2 == 0:
            raise Exception("row count should be even")
        self.rows = rows

    def to_screen_system(self, ij_index):
        rows = self.rows

        cut = rows // 2

        x, y = ij_index

        if x < cut:
            tx = (x * 2) + 1 - y
        else:
            tx = rows - y

        if x < cut:
            ty = y
        else:
            ty = (x - cut) * 2 + 1 + y

        return (tx, ty)

    def to_file_system(self, xy):
        tx, ty = xy

        cut = self.rows // 2

        raise NotImplementedError()

    def get_size_of_row(self, i):
        if i < (self.rows//2):
            return (i * 2) + 2
        else:
            return (((self.rows//2) - (i - (self.rows//2)) - 1) * 2) + 2

    def retrieve_diamond_indices(self, top_ij_coord, size):
        si, sj = top_ij_coord
        ssize = self.get_size_of_row(si)

        indices = []

        for i in range(size):
            for j in range(size):

                ni = si + i
                nj = sj + j

                if ni > self.rows:
                    raise Exception("i is out of bounds: ({}, {})".format(ni, nj))

                ni_size = self.get_size_of_row(ni)

                size_diff = ni_size - ssize

                nj += (size_diff // 2)

                if nj > ni_size:
                    raise Exception("j is out of bounds: ({}, {})".format(ni, nj))

                indices.append((ni, nj))

        return indices


class TiledDiamondSystem(DiamondSystem):

    def __init__(self, tilewidth=32, tileheight=16, rows=400, xoffset=16, yoffset=16):
        self.tilewidth = tilewidth
        self.tileheight = tileheight
        self.rows = rows
        self.xoffset = xoffset
        self.yoffset = yoffset

    def to_screen_system(self, ij_index):
        i, j = super().to_screen_system(ij_index)
        return (i * (self.tilewidth // 2), j * (self.tileheight // 2))

    def system_tile_coordinates(self, ij_index):
        i, j = self.to_screen_system(ij_index)
        xoff = i + self.xoffset
        yoff = j + self.yoffset
        width = self.tilewidth
        height = self.tileheight
        return [(xoff, yoff), (xoff + width // 2, yoff + height // 2), (xoff, yoff + height),
                (xoff - width // 2, yoff + height // 2)]


def build_palette(uniq):

    mapping = sorted(list(uniq))
    pal = palette.create_palette(len(mapping))

    return (mapping, pal)


def make_image_of_data(dt, system: TiledDiamondSystem = TiledDiamondSystem()) -> Image.Image:
    width = int(system.rows * system.tilewidth * 0.5) + 32
    height = int(system.rows * system.tileheight * 0.5) + 32
    im = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(im)
    mapping, pal = build_palette(set(x for y in dt for x in y))

    for i in range(len(dt)):
        for j in range(len(dt[i])):
            coords = system.system_tile_coordinates((i, j))
            coords = [(im.width - coord[0], coord[1]) for coord in coords]
            draw.polygon(coords, outline=None, fill=pal[mapping.index(dt[i][j])])

    return im