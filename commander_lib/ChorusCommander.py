# -*- coding: utf-8 -*-
import os
from StringIO import StringIO
import codecs
import pandas
from pandas.parser import CParserError
from Log import logger
from ChorusAPI import ChorusAPI
import time

class ChorusCommander():
    def __init__(self, session_id, datasource_name,
                 chorus_address=os.getenv("CHORUS_ADDRESS", "http://localhost:8080")):
        self.chorus_api = ChorusAPI(session_id, chorus_address)
        self.datasource_name = datasource_name
        self.database_name = "default"
        self.schema_name = None

    def hdfs_ls(self, file_path, **kwargs):
        """Lists files in HDFS.

        Args:
            file_path: A file path in HDFS.
            **kwargs: Arbitrary key-value pairs.
                For example: ``verify=False`` means do not verify the SSL
                certificate if SSL is enabled.

        Returns:
            A list of files in that file path.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """
        response = self.chorus_api.hdfs_ls(self.datasource_name, file_path, **kwargs)
        if response.status_code >= 500:
            raise Exception("Server Error")

        if response.status_code not in range(200, 300):
            raise Exception(response.reason + "\n" + response.content)

        files = [['filename', 'size', 'content_count', 'is_dir']]
        for file in response.json():
            files.append([file['path'], file['size'], file['content_count'], file['is_directory']])

        return pandas.DataFrame.from_records(files[1:], columns=files[0])

    def read_file_csv(self, file_path,
                      sep=',',
                      delimiter=None,
                      header=None,
                      names=None,
                      index_col=None,
                      usecols=None,
                      squeeze=False,
                      prefix=None,
                      mangle_dupe_cols=True,
                      dtype=None,
                      engine=None,
                      converters=None,
                      true_values=None,
                      false_values=None,
                      skipinitialspace=False,
                      skiprows=None,
                      skipfooter=None,
                      nrows=None,
                      na_values=None,
                      keep_default_na=True,
                      na_filter=True,
                      verbose=False,
                      skip_blank_lines=True,
                      parse_dates=False,
                      infer_datetime_format=False,
                      keep_date_col=False,
                      date_parser=None,
                      dayfirst=False,
                      iterator=False,
                      chunksize=None,
                      compression=None,
                      thousands=None,
                      decimal='.',
                      lineterminator=None,
                      quotechar='"',
                      quoting=0,
                      escapechar="\\",
                      comment=None,
                      encoding='utf-8',
                      dialect=None,
                      tupleize_cols=False,
                      error_bad_lines=True,
                      warn_bad_lines=True,
                      skip_footer=0,
                      doublequote=True,
                      delim_whitespace=False,
                      as_recarray=False,
                      compact_ints=False,
                      use_unsigned=False,
                      low_memory=True,
                      buffer_lines=None,
                      memory_map=False,
                      float_precision=None,
                      **kwargs):
        """Accesses a file on HDFS, and reads it into a DataFrame in pandas
        using the ``pandas.read_csv`` function. This function also supports
        optionally iterating or breaking the file into chunks.

        Additional information can be found in the
        `IO Tools help <http://pandas.pydata.org/pandas-docs/stable/io.html>`_.

        Args:
            file_path: The full path of the file in HDFS.
            sep (str): Delimiter to use. Default is ','. If ``sep`` is
                ``None``, the function will try to automatically determine
                this. Separators longer than 1 character and different from
                's+' will be interpreted as regular expressions. This will
                force use of the Python parsing engine and will ignore quotes
                in the data. Regex example: 'rt'
            delimiter (str): Alternative argument name for ``sep``. Default is
                ``None``.
            header (int or list of ints): Row number(s) to use as the column
                names. This number also refers to the start of the data. The
                default value is 0 if no numbers are passed. To replace
                existing names, use ``header=0``. The header can be a list of
                integers that specify row locations for a mutli-index on the
                columns. For example, the list [0,1,3] would skip row 2. Note
                that this parameter ignores commented lines and empty lines if
                ``skip_blank_lines=True``. In this case, ``header=0`` denotes
                the first line of data rather than the first line of the file.
                Default value is 'infer'; this means that the header row will
                be automatically inferred.
            names: List of column names to use. Default value is ``None``. If
                the file contains no header row, then explicitly pass
                ``header=None``.
            index_col (int, sequence, or False): Column to use as the row
                labels of the DataFrame. If a sequence is given, a MultiIndex
                is used. If you have a malformed file with delimiters at the
                end of each line, use ``index_col=False`` to force pandas _not_
                to use the first column as the index for row names. Default
                value is ``None``.
            usecols (array-like): Return a subset of the columns. All elements
                in this array must either be positional (such as integer
                indices into the document columns) or strings that correspond
                to column names provided either by the user in ``names`` or
                inferred from the document header row(s). For example, a valid
                ``usecols`` parameter would be [0,1,2] or ['foo','bar','baz'].
                Using this parameter results in much faster parsing time and
                lower memory usage. Default value is ``None``.
            squeeze (boolean): If the parsed data only contains one column,
                then return a Series. Default value is ``False``.
            prefix (str): Prefix to add column numbers when there is no header.
                For example, 'X' would be added to each column number to
                become 'X0','X1',...
                Default value is ``None``.
            mangle_dupe_cols (boolean): Duplicate columns will be specified as
                'X.0'...'X.N', rather than 'X'...'X'
                Default value is ``True``.
            dtype (Type name or dict of column -> type): Data type for data or
                columns. E.g. ``{‘a’: np.float64, ‘b’: np.int32}`` (Unsupported
                with engine=’python’). Use a ``str`` or ``object`` to preserve
                and not interpret dtype.
            engine (Optional): ``{'c', 'python'}``. Parser enginge to use. The
                C engine is faster, while the python engine is currently more
                feature-complete.
            converters (dict): Dict of functions for converting values in
                in certain columns. Keys can either be integers or column
                labels. Default value is ``None``.
            true_values (list): Values to consider as ``True``. Default value
                is ``None``.
            false_values (list): Values to consider as ``False``. Default value
                is ``None``.
            skipinitialspace (boolean): Skip spaces after delimiter. Default
                value is ``False``.
            skiprows (list-like or integer): Line numbers to skip (0-indexed)
                or number of lines to skip (integer) at the start of the file.
                Default value is ``None``.
            skipfooter (int): Number of lines at the bottom of hte file to skip
                (Unsupported with ``engine=c``). Default value is 0.
            nrows (int): Number of rows of the file to read. Useful for reading
                pieces of large files. Default value is ``None``.
            na_values (str or list-like or dict): Additional strings to
                recognize as NA/NaN. If dict passed, specific per-column NA
                values. By default the following values are interpreted as NaN:
                '', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN',
                '-nan', '1.#IND', '1.#QNAN', 'N/A', 'NA', 'NULL', 'NaN', 'nan'.
                Default value is ``None``.
            keep_default_na (bool): If ``na_values`` are specified and
                ``keep_default_na`` is ``False``, the default NaN values are
                overriden, otherwise they are appended to. Default value is
                ``True``.
            na_filter (boolean): Detect missing value markers (empty strings
                and the value of ``na_values``). In data without any NAs,
                passing ``na_filter=False`` can impprove the performance of
                reading a large file. Default value is ``True``.
            verbose (boolean): Indicate the number of NA values placed in
                non-numeric columns. Default value is ``False``.
            skip_blank_lines (boolean): If ``True``, skip over blank lines
                rather than interpreting them as NaN values. Default value is
                ``True``.
            parse_dates (boolean or list of ints or list of lists or dict):
                - If boolean: If ``True``, then try parsing the index.
                - If list of ints or names: For example, if [1,2,3], then try
                parsing columns 1,2,3 each as a separate date column.
                - If list of lists: For example, if [[1,3]], then combine
                columns 1 and 3 and parse as a single date column.
                - If dict: For example, if {‘foo’ : [1, 3]}, then parse columns
                1,3 as date and call result ``foo``. Note: a fast-path exists
                for iso8601-formatted dates.
                - Default value is ``False``.
            infer_datetime_format (boolean): If ``True`` and ``parse_dates`` is
                enabled for a column, then attempt to infer the datetime format
                to speed up the processing. Default value is ``False``.
            keep_date_col (boolean): If ``True`` and ``parse_dates`` specifies
                combining multiple columns, then keep the original columns.
                Default value is ``False``.
            date_parser (function): Function to use for converting a sequence
                of string columns to an array of datetime instances. The
                default uses ``dateutil.parser.parser`` to do the conversion.
                Pandas will try to call ``date_parser`` in three different
                ways, advancing to the next if an exception occurs:
                1) Pass one or more arrays (as defined by ``parse_dates``) as
                arguments;
                2) concatenate (row-wise) the string values from the columns
                defined by ``parse_dates`` into a single array and pass that;
                and
                3) call ``date_parser`` once for each row using one or more
                strings (corresponding to the columns defined by
                ``parse_dates``) as arguments.
                Default value is ``None``.
            dayfirst (boolean): DD/MM format dates. This is the international
                and European format. Default value is ``False``.
            iterator (boolean): Return a ``TextFileReader`` object for
                iteration or getting file chunks with ``get_chunk()``. Default
                value is ``False``.
            chunksize (int): Return a ``TextFileReader`` object for iteration.
                See IO Tools docs for more information on iterator and
                chunksize. Default value is ``None``.
            compression: ``{‘infer’, ‘gzip’, ‘bz2’, None}``. For on-the-fly
                decompression of on-disk date. If 'infer', then use gzip or bz2
                if ``filepath_or_buffer`` is a string ending in '.gz' or
                '.bz2', respectively. No decompression otherwise. Set to
                ``None`` for no decompression. Default value is 'infer'.
            thousands (str): Thousands separator. Default value is ``None``.
            decimal (str): Character to recognize as a decimal point. (For
                example, use ',' for European data). Default value is '.'
            lineterminator (str - length 1): Character to break file into
                lines. Only valid with C parser. Default value is ``None``.
            quotechar (str - length 1, Optional): The character used to denote
                the start and end of a quoted item. Quoted items can include
                the delimiter and it will be ignored.
            quoting (int or csv.QUOTE_* instance): Control field quoting
                behavior per ``csv.QUOTE_*`` constants. Use one of
                QUOTE_MINIMAL (0), QUOTE_ALL (1), QUOTE_NONNUMERIC (2) or
                QUOTE_NONE (3). Default (``None``) results in QUOTE_MINIMAL
                behavior.
            escapechar (str - length 1): One-character string used to
                escapechar delimiter when quoting is QUOTE_NONE. Default value
                is ``\``.
            comment (str): A character which indicates the remainder of line
                should not be parsed. If this is found at the beginning of a
                line, the line will be ignored altogether. This parameter must
                be a single character. Like empty lines (as long as
                ``skip_blank_lines=True``), fully commented lines are ignored
                by the parameter header but not by ``skiprows``. For example,
                if ``comment='#``, parsing
                '#empty
                a,b,c
                1,2,3'
                with ``header=0`` will result in 'a,b,c' being treated as the
                header. Default value is ``None``.
            encoding (str): Encoding to use for UTF when reading/writing
                (ex. ‘utf-8’). List of Python standard encodings can be found
                at
                https://docs.python.org/3/library/codecs.html#standard-encodings
                Default value is ``utf-8``.
            dialect (str or csv.Dialect): If ``None``, then it defaults to the
                Excel dialect. Ignored if ``sep`` is longer than 1 char. See
                ``csv.Dialect`` documentation for more details. Default value
                is ``None``.
            tupleize_cols (boolean): Leave a list of tuples on columns as-is.
                The default is to convert to a MultiIndex on the columns.
                Default value is ``False``.
            error_bad_lines (boolean): Lines with too many fields (e.g. a csv
                line with too many commas) will by default cause an exception
                to be raised, and no DataFrame will be returned. If ``False``,
                then these "bad lines" will be dropped from the DataFrame that
                is returned. (Only valid with C parser). Default value is
                ``True``.
            warn_bad_lines (boolean): If ``error_bad_lines`` is ``False``, and
                ``warn_bad_lines`` is ``True``, a warning for each "bad line"
                will be output. (Only valid with C parser). Default value is
                ``True``.
            **kwargs: arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL cert when SSL is enabled.

        Returns:
            pandas.DataFrame: return a pandas DataFrame.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """

        response = self.chorus_api.get_data_from_hdfs_datasource(self.datasource_name, file_path, **kwargs)

        if response.status_code >= 500:
            raise Exception("Server Error")

        if response.status_code not in range(200, 300):
            raise Exception(response.reason + "\n" + response.content)


        data = response.json()
        tmp_path = "./.%s-%s" % (os.path.basename(file_path), time.time())
        try:
            with codecs.open(tmp_path, encoding=encoding, mode='w') as f:
                f.write(data['data'])
            dataFrame = pandas.read_csv(tmp_path,
                                        sep=sep,
                                        delimiter=delimiter,
                                        header=header,
                                        names=names,
                                        index_col=index_col,
                                        usecols=usecols,
                                        squeeze=squeeze,
                                        prefix=prefix,
                                        mangle_dupe_cols=mangle_dupe_cols,
                                        dtype=dtype,
                                        engine=engine,
                                        converters=converters,
                                        true_values=true_values,
                                        false_values=false_values,
                                        skipinitialspace=skipinitialspace,
                                        skiprows=skiprows,
                                        skipfooter=skipfooter,
                                        nrows=nrows,
                                        na_values=na_values,
                                        keep_default_na=keep_default_na,
                                        na_filter=na_filter,
                                        verbose=verbose,
                                        skip_blank_lines=skip_blank_lines,
                                        parse_dates=parse_dates,
                                        infer_datetime_format=infer_datetime_format,
                                        keep_date_col=keep_date_col,
                                        date_parser=date_parser,
                                        dayfirst=dayfirst,
                                        iterator=iterator,
                                        chunksize=chunksize,
                                        compression=compression,
                                        thousands=thousands,
                                        decimal=decimal,
                                        lineterminator=lineterminator,
                                        quotechar=quotechar,
                                        quoting=quoting,
                                        escapechar=escapechar,
                                        comment=comment,
                                        encoding=encoding,
                                        dialect=dialect,
                                        tupleize_cols=tupleize_cols,
                                        error_bad_lines=error_bad_lines,
                                        warn_bad_lines=warn_bad_lines,
                                        skip_footer=skip_footer,
                                        doublequote=doublequote,
                                        delim_whitespace=delim_whitespace,
                                        as_recarray=as_recarray,
                                        compact_ints=compact_ints,
                                        use_unsigned=use_unsigned,
                                        low_memory=low_memory,
                                        buffer_lines=buffer_lines,
                                        memory_map=memory_map,
                                        float_precision=float_precision)
        except CParserError as e:
            raise Exception(e.message + "\n Input format not supported")
        finally:
            os.remove(tmp_path)

        return dataFrame

    def write_file_csv(self, data_frame,
               file_path,
               overwrite_exists=False,
               sep=',',
               na_rep='',
               float_format=None,
               columns=None,
               header=True,
               index=False,
               index_label=None,
               encoding=None,
               compression=None,
               quoting=None,
               quotechar='"',
               line_terminator='\n',
               chunksize=None,
               tupleize_cols=False,
               date_format=None,
               doublequote=True,
               escapechar=None,
               decimal='.',
               **kwargs):
        """Write the contents in a pandas DataFrame to an HDFS path. The data
        format will be CSV format by default.

        Args:
            data_frame: The pandas DataFrame object.
            file_path: The full destination path in HDFS.
            sep (char): Field delimiter for the output file.
                Default value is ','.
            na_rep (str): Missing data representation. Default value is ''.
            float_format (str): Format string for floating-point numbers.
                Default value is ``None``.
            columns (sequence, optional): Columns to write.
            header (boolean or list of string): Write out column names. If a
                list of string is given, it is assumed to contain aliases for
                the column names. Default value is ``True``.
            index (boolean): Write row names (index). Default value is
                ``True``.
            index_label (string or sequence or False): Column label for index
                column(s) if desired. If ``None`` is given, and ``header`` and
                ``index`` are ``True``, then the index names are used. A
                sequence should be given if the DataFrame uses MultiIndex. If
                ``False``, do not print fields for index names. Use
                ``index_label=False`` for easier importing in R.
            encoding (str, optional): A string representing the encoding to
                use in the output file, defaults to 'ascii' on Python 2 and
                'utf-8' on Python 3.
            compression (str, optional): a string representing the compression
                to use in the output file, allowed values are 'gzip', 'bz2'
            line_terminator (str): The newline character or character sequence
                to use in the output file. Default value is 'n'.
            quoting (constant from csv module): Defaults to csv.QUOTE_MINIMAL.
            quotechar (string - length 1): character used to quote fields.
                Default value is '"'.
            doublequote (boolean): Control quoting of ``quotechar`` inside a
                field. Default value is ``True``.
            escapechar (string - length 1): character used to escape ``sep``
                and ``quotechar`` when appropriate. Default value is ``None``.
            chunksize (int or None): rows to write at a time.
            tupleize_cols (boolean): write MultiIndex columns as a list of
                tuples (if ``True``), or new, expanded format if ``False``.
                Default value is ``False``.
            date_format (str): Format string for datetime objects. Default
                value is ``None``.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """

        try:
            buffers = data_frame.to_csv(None,
                                        sep=sep,
                                        na_rep=na_rep,
                                        float_format=float_format,
                                        columns=columns,
                                        header=header,
                                        index=index,
                                        index_label=index_label,
                                        encoding=encoding,
                                        compression=compression,
                                        quoting=quoting,
                                        quotechar=quotechar,
                                        line_terminator=line_terminator,
                                        chunksize=chunksize,
                                        tupleize_cols=tupleize_cols,
                                        date_format=date_format,
                                        doublequote=doublequote,
                                        escapechar=escapechar,
                                        decimal=decimal,
                                        **kwargs)
        except CParserError as e:
            raise Exception(e.message + "\n Input format not supported")

        self.write_file(buffers, file_path, overwrite_exists, **kwargs)

    def write_file(self, content, file_path, overwrite_exists=False, **kwargs):
        """Writes the content to the HDFS file path.

        Args:
            content: The content to write to file.
            file_path: The target file path.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """

        lens = 0
        try:
            lens = len(self.hdfs_ls(file_path))
        except:
            pass
        if lens == 1 and not overwrite_exists:
            raise Exception("%s already exists, and overwrite_exists flag is equal to False." % file_path)
        if lens > 1:
            raise Exception("%s is an existing directory." % file_path)

        response = self.chorus_api.import_data_to_hdfs_datasource(self.datasource_name, content, file_path, **kwargs)

        if response.status_code >= 500:
            raise Exception("Server Error")

        if response.status_code not in range(200, 300):
            raise Exception(response.reason + "\n" + response.content)

    def _get_table_path(self, table_name, schema_name, database_name, is_hive=False):
        if schema_name is None or schema_name is "":
            schema_name = self.schema_name
        if database_name is None or database_name is "":
            database_name = self.database_name

        table_path = filter(lambda x: x is not None and x is not "", [database_name, schema_name, table_name])
        if not is_hive:
            table_path = '"' + '"."'.join(table_path) + '"'
        else:
            table_path = '.'.join(table_path)

        return (database_name, schema_name, table_path)

    def sql_execute(self, sql, schema_name=None, database_name=None, **kwargs):
        """General SQL execute. If the ``schema_name`` and ``database_name``
            are not specified, it will use the one set in
            ``self.database_name`` and ``self.schema_name``.

        Args:
            sql: The SQL to be executed.
            schema_name (str): The schema name (Can be ``None``, some databases
                have no schema). Default value is ``None``.
            database_name (str): The database name. Default value is ``None``.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.

        Returns:
            JSON object from Chorus API response.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """

        database_name, schema_name, table_path = self._get_table_path("dummy", schema_name, database_name, kwargs.get("is_hive", False))

        assert (sql is not None and database_name is not None)
        assert (sql != "" and database_name != "")

        response = self.chorus_api.sql_execute(self.datasource_name, sql, schema_name=schema_name, database_name=database_name, **kwargs)

        if response.status_code >= 500:
            raise Exception("Server Error")

        if response.status_code is not 201:
            raise Exception(response.reason + "\n" + response.content)

        response = response.json()
        col_names = None
        if response['response'].has_key("columns"):
            col_names = [c['name'] for c in response['response']['columns']]
        if response['response'].has_key("rows"):
            data = response['response']['rows']
            df = pandas.DataFrame.from_records(data=data, columns=col_names)
            return df.convert_objects(convert_numeric=True)
        else:
            return response

    def _table_exists(self, table_path, schema_name=None, database_name=None, **kwargs):

        try:
            sql = "SELECT * FROM %s LIMIT 1" % table_path
            self.sql_execute(sql, schema_name, database_name, **kwargs)
            return True
        except:
            return False

    def read_table(self, table_name, schema_name=None, database_name=None, **kwargs):
        """Get the contents of the table wrapped in a pandas DataFrame.

        Args:
            table_name (str): The table name.
            schema_name: The schema name (Can be ``None``, some databases have
                no schema). Default value is ``None``.
            database_name (str): The database name. Default value is ``default``.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.

        Returns:
            pandas.DataFrame: Return a pandas DataFrame.

        Raises:
            Exception: An error occured when contacting the Chorus API.
        """
        database_name, schema_name, table_path = self._get_table_path(table_name, schema_name, database_name, kwargs.get("is_hive", False))

        sql = 'select * from %s' % (table_path)
        data = self.sql_execute(sql, schema_name, database_name, **kwargs)
        return data

    def create_table(self, table_name, column_info, schema_name=None, database_name=None, drop_if_exists=False, **kwargs):
        """Creates a table.

        Args:
            table_name (str): The name of the table.
            column_info: A list of dictionary defining the ``column_name`` and
                ``column_type``.
                Examples:
                ``[{"foo":"int"}, {"bar":"varchar(50)"}]``
                Default value is ``None``.
            schema_name (str): The schema name (Can be ``None``, some databases
                have no schema). Default value is ``None``.
            database_name (str): The database name. Default value is ``default``.
            drop_if_exists (boolean): Whether to drop the table if the table
                already exists. If set to ``False``, the data will be appended
                to the existing table. Default value is ``False``.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.

        Returns:
            True if table created otherwise False.
        """
        database_name, schema_name, table_path = self._get_table_path(table_name, schema_name, database_name, kwargs.get("is_hive", False))

        if self._table_exists(table_path, schema_name, database_name):
            if drop_if_exists:
                sql = "DROP TABLE %s" % table_path
                self.sql_execute(sql, schema_name, database_name, **kwargs)
            else:
                logger.warning("%s already exists and drop_if_exists set to False, table will not be created" % table_path)
                return False

        sql = "CREATE TABLE %s ( %s )" % (table_path, ",\n".join(map(lambda x: "\t".join(x.items()[0]), column_info)))
        self.sql_execute(sql, schema_name, database_name, **kwargs)
        return True

    def write_table(self,
                    data_frame,
                    table_name,
                    column_info=None,
                    schema_name=None,
                    database_name=None,
                    drop_if_exists=False,
                    append_if_exists=False,
                    limit = 1000,
                    **kwargs):

        """Import the contents in a pandas DataFrame to the table in the
        database.

        Args:
            data_frame: The pandas DataFrame object.
            table_name (str): The table name.
            column_info: A list of dictionary defining the ``column_name`` and
                ``column_type``.
                Examples:
                ``[{"foo":"int"}, {"bar":"varchar(50)"}]``
                Default value is ``None``.
            schema_name (str): The schema name (Can be ``None``, some databases
                have no schema). Default value is ``None``.
            database_name (str): The database name. Default value is ``None``.
            drop_if_exists (boolean): Whether to drop the table if the table
                already exists. If set to ``False``, nothing happens. Default
                value is ``False``.
            append_if_exists (boolean): Whether to append the table if the table
                already exists. If set to ``False``, nothing happens. Default
                value is ``False``.
            limit (int): The number of rows in the DataFrame that need to be
                written into the table. Default value is ``1000``.
            **kwargs: Arbitrary key-value pairs. For example: ``verify=False``
                means do not verify the SSL certificate when SSL is enabled.
        """
        database_name, schema_name, table_path = self._get_table_path(table_name, schema_name, database_name, kwargs.get("is_hive", False))

        if column_info is None:
            column_info = map(lambda x: {x[0]: self._transfer_dtype_to_db_type(x[1])}, zip(data_frame.columns.get_values(), data_frame.dtypes))
        flag = self.create_table(table_name, column_info, schema_name, database_name, drop_if_exists, **kwargs)
        if flag is False and append_if_exists is False:
            logger.warning("nothing write into %s, the append_if_exists is set to False" % table_path)
            return
        rows = len(data_frame)
        if rows <= 1:
            logger.warning("nothing write into %s, because no data found in dataframe" % table_path)
            return

        if rows > limit:
            logger.warning("inserted data exceed %s, will only insert %s rows" % (limit, limit))
        sql = "INSERT INTO %s (%s) VALUES %s" % (table_path, ",".join(map(lambda x: x.keys()[0], column_info)),
                                                 ",\n".join(map(lambda x: "('%s')" % "', '".join(map(str, x[1:])), list(data_frame.itertuples())[:limit])))
        self.sql_execute(sql, schema_name, database_name, **kwargs)

    def _transfer_dtype_to_db_type(self, dtype):
        if dtype.name.startswith("int"):
            return "INTEGER"
        elif dtype.name.startswith("float"):
            return "FLOAT"
        elif dtype.name.startswith("bool"):
            return "BOOLEAN"
        else:
            return "VARCHAR(50)"

if __name__ == "__main__":
    # chorus_commander = ChorusCommander("70983f6163995e5a2102c6d308fbeec99aa645a4", "CDH5_HA",
    #                                    chorus_address="http://localhost:8080")
    # df = chorus_commander.read_file_csv("/automation_test_data/parquet/apple_customers_parquet/", header=0,
    #                                     max="5", verify=False)
    # print df
    # chorus_commander.write_file("dddd", "/tm/hao_test2.csv")
    # df = chorus_commander.read_file_csv("/tm/hao_test2.csv")
    # print df
    # chorus_commander.write_file(df, "/aaa", index=False)
    #chorus_commander = ChorusCommander("96d15175aa415e7e2118b0fe35452a3d87f75d26", "HAWQ1.3_PHD3.0",
    #                                   chorus_address="http://localhost:8080")
    #df = chorus_commander.read_table("adult", schema_name="demo", database_name="miner_demo", max="10")
    #print df

    cc = ChorusCommander("64873948edd9a42821a5db7fefb2cf9ce75dc229", "hawq", chorus_address="http://localhost:8080")

    #cc = ChorusCommander("7e0d8d046a3a059dccc2a8e30c7f7552575977ca", "HAWQ1.3_PHD3.0", chorus_address="http://localhost:8080")
    db_df_credit = cc.read_table(table_name='credit', schema_name='demo', database_name='miner_demo')
    cc.write_table(db_df_credit, "testtttt", schema_name='demo', database_name='miner_demo')
