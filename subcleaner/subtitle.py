from .sub_block import SubBlock


class Subtitle(object):
    blocks: list

    def __init__(self, file_content: str):
        self.blocks: list = list()
        self._parse(file_content)

    def add_block(self, block: SubBlock) -> None:
        self.blocks.append(block)

    def remove_block(self, block: SubBlock) -> None:
        self.blocks.remove(block)

    def _parse(self, file_content: str) -> None:
        current_index = 1
        block = SubBlock(1)
        for line in file_content.split("\n"):
            if len(line) == 0:
                if len(block.content) > 0:
                    self.blocks.append(block)
                    current_index += 1
                    block = SubBlock(current_index)
                continue

            if " --> " in line and block.stop_time.seconds == 0:
                start_string = line.split(" --> ")[0].rstrip()[:12]
                block.set_start_time(start_string)

                stop_string = line.split(" --> ")[1].rstrip()[:12]
                block.set_stop_time(stop_string)
                continue

            if block.stop_time.seconds == 0:
                continue

            block.content = block.content + line + "\n"

    def __repr__(self):
        sub_file_content = ""
        for i in range(len(self.blocks)):
            sub_file_content += (str(i+1) + "\n")
            sub_file_content += (str(self.blocks[i]))
            sub_file_content += "\n"
        return sub_file_content[:-1]
