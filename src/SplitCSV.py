import pandas as pd

# csv file name to be read in
in_csv = '/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/implementation/features/flow_0.csv'

# get the number of lines of the csv file to be read
number_lines = sum(1 for row in (open(in_csv)))

# size of rows of data to write to the csv,
# you can change the row size according to your need
rowsize = 2000
header = ['src_ip','dst_ip','src_port','dst_port','protocol','timestamp','flow_duration','flow_byts_s','flow_pkts_s','fwd_pkts_s','bwd_pkts_s','tot_fwd_pkts','tot_bwd_pkts','totlen_fwd_pkts',
        'totlen_bwd_pkts','fwd_pkt_len_max','fwd_pkt_len_min','fwd_pkt_len_mean','fwd_pkt_len_std','bwd_pkt_len_max','bwd_pkt_len_min','bwd_pkt_len_mean',
        'bwd_pkt_len_std','pkt_len_max','pkt_len_min','pkt_len_mean','pkt_len_std','pkt_len_var','fwd_header_len','bwd_header_len','fwd_seg_size_min',
        'fwd_act_data_pkts','flow_iat_mean','flow_iat_max','flow_iat_min','flow_iat_std','fwd_iat_tot','fwd_iat_max','fwd_iat_min','fwd_iat_mean','fwd_iat_std',
        'bwd_iat_tot','bwd_iat_max','bwd_iat_min','bwd_iat_mean','bwd_iat_std','fwd_psh_flags','bwd_psh_flags','fwd_urg_flags','bwd_urg_flags','fin_flag_cnt',
        'syn_flag_cnt','rst_flag_cnt','psh_flag_cnt','ack_flag_cnt','urg_flag_cnt','ece_flag_cnt','down_up_ratio','pkt_size_avg','init_fwd_win_byts','init_bwd_win_byts',
        'active_max','active_min','active_mean','active_std','idle_max','idle_min','idle_mean','idle_std','fwd_byts_b_avg','fwd_pkts_b_avg','bwd_byts_b_avg',
        'bwd_pkts_b_avg','fwd_blk_rate_avg','bwd_blk_rate_avg','fwd_seg_size_avg','bwd_seg_size_avg','cwe_flag_count','subflow_fwd_pkts','subflow_bwd_pkts',
        'subflow_fwd_byts','subflow_bwd_byts']
max_size = round(number_lines / rowsize)
# start looping through data writing it to a new file for each set
for i in range(1, max_size, 1):
        df = pd.read_csv(
            in_csv,
            names=header,
            nrows=rowsize,  # number of rows to read at each loop
            skiprows=i)  # skip rows that have been read
        # csv to write data to a new file with indexed name. input_1.csv etc.
        out_csv = '/home/steven/Documents/UdeA/maestria/Tesis/Implementación/my_project/my_environment/code/implementation/features/flow_' + str(i) + '.csv'

        df.to_csv(
            out_csv,
            index=False,
            mode='a',  # append data to csv file
            chunksize=rowsize)  # size of data to append for each loop
