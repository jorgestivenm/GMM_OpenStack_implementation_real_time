sudo .venv/bin/python3.8 SniffAndSave.py 


#modifying the utils.py from cicflowmeter
"""
def get_statistics(alist: list):
    """Get summary statistics of a list"""
    iat = dict()

    if len(alist) > 1:
        iat["total"] = sum(alist)
        iat["max"] = max(alist)
        iat["min"] = min(alist)
        alist2 =[]
        for i in alist:
            alist2.append(int(i))
        iat["mean"] = numpy.mean(alist2)
        iat["std"] = numpy.sqrt(numpy.var(alist2))
    else:
        iat["total"] = 0
        iat["max"] = 0
        iat["min"] = 0
        iat["mean"] = 0
        iat["std"] = 0

    return iat
"""

#modifying the flow_bytes.py from cicflowmeter.features

"""
    def get_min_forward_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the opposite direction as the flow.

        Returns:
            int: The amount of bytes.

        """
        def header_size(packets):
            hz = []
            for packet, direction in packets:
                if direction == PacketDirection.FORWARD:
                    hz.append(self._header_size(packet))
            return hz

        packets = self.feature.packets

        v  = header_size(packets)
        if not v :
            return 0
        else:
            return min(v)
"""